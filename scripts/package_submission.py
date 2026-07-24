"""Package and cryptographically verify the final assessment submission."""

from __future__ import annotations

import hashlib
import json
import subprocess
import zipfile
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUBMISSION = ROOT / "submission"
DIST = ROOT / "dist"
ARCHIVE_ROOT = "MSE802_Assessment2_Submission"
ARCHIVE = DIST / f"{ARCHIVE_ROOT}.zip"
ARCHIVE_CHECKSUM = DIST / f"{ARCHIVE_ROOT}.sha256"
MANIFEST = DIST / f"{ARCHIVE_ROOT}_MANIFEST.sha256"
VALIDATION = DIST / "FINAL_VALIDATION.json"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_output(*arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def main() -> None:
    branch = git_output("branch", "--show-current")
    if branch != "task":
        raise RuntimeError(f"Packaging is restricted to branch 'task', found {branch!r}")

    files = sorted(
        (path for path in SUBMISSION.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(SUBMISSION).as_posix(),
    )
    if not files:
        raise RuntimeError("The submission folder is empty")
    if any(path.is_symlink() for path in files):
        raise RuntimeError("Symbolic links are not allowed in the submission")

    source_hashes = {
        f"{ARCHIVE_ROOT}/{path.relative_to(SUBMISSION).as_posix()}": sha256_file(
            path
        )
        for path in files
    }

    DIST.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(
        ARCHIVE,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for path in files:
            archive_name = (
                f"{ARCHIVE_ROOT}/{path.relative_to(SUBMISSION).as_posix()}"
            )
            archive.write(path, archive_name)

    with zipfile.ZipFile(ARCHIVE) as archive:
        archive_error = archive.testzip()
        archive_names = sorted(archive.namelist())
        expected_names = sorted(source_hashes)
        content_hashes_match = all(
            sha256_bytes(archive.read(name)) == source_hashes[name]
            for name in expected_names
        )

    entry_set_matches = archive_names == expected_names
    archive_opens = archive_error is None
    passed = archive_opens and entry_set_matches and content_hashes_match
    if not passed:
        raise RuntimeError(
            "ZIP verification failed: "
            f"archive_opens={archive_opens}, "
            f"entry_set_matches={entry_set_matches}, "
            f"content_hashes_match={content_hashes_match}"
        )

    MANIFEST.write_text(
        "\n".join(
            f"{digest}  {name}" for name, digest in source_hashes.items()
        )
        + "\n",
        encoding="utf-8",
    )
    archive_digest = sha256_file(ARCHIVE)
    ARCHIVE_CHECKSUM.write_text(
        f"{archive_digest}  {ARCHIVE.name}\n",
        encoding="utf-8",
    )

    a2_commit_count = int(
        git_output("rev-list", "--count", "--grep=^A2-", "HEAD")
    )
    result = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "status": "PASS",
        "branch": branch,
        "source_parent_commit": git_output("rev-parse", "HEAD"),
        "a2_commit_count_before_final_commit": a2_commit_count,
        "expected_a2_commit_count_after_final_commit": a2_commit_count + 1,
        "archive": ARCHIVE.name,
        "archive_size_bytes": ARCHIVE.stat().st_size,
        "archive_sha256": archive_digest,
        "manifest": MANIFEST.name,
        "file_count": len(files),
        "checks": {
            "archive_opens": archive_opens,
            "entry_set_matches_submission": entry_set_matches,
            "content_hashes_match_manifest": content_hashes_match,
            "privacy_audit_pass": json.loads(
                (SUBMISSION / "PRIVACY_AUDIT.json").read_text(encoding="utf-8")
            )["summary"]["status"]
            == "PASS",
            "submission_audit_pass": json.loads(
                (SUBMISSION / "SUBMISSION_AUDIT.json").read_text(encoding="utf-8")
            )["summary"]["status"]
            == "PASS",
        },
    }
    if not all(result["checks"].values()):
        raise RuntimeError(f"Final validation failed: {result['checks']}")
    VALIDATION.write_text(
        json.dumps(result, indent=2) + "\n",
        encoding="utf-8",
    )

    print(
        f"Final package: PASS ({len(files)} files, "
        f"{ARCHIVE.stat().st_size:,} bytes)"
    )
    print(f"ZIP SHA-256: {archive_digest}")


if __name__ == "__main__":
    main()
