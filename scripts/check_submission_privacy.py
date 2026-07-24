"""Scan the submission folder for credentials and local/private artifacts.

Only finding types and relative paths are reported; matched values are never
written to the console or audit file.
"""

from __future__ import annotations

import json
import re
import sys
import zipfile
from datetime import UTC, datetime
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SUBMISSION = ROOT / "submission"
OUTPUT = SUBMISSION / "PRIVACY_AUDIT.json"

FORBIDDEN_NAMES = {
    ".env",
    ".envrc",
    ".git",
    ".ipynb_checkpoints",
    ".venv",
    "__pycache__",
    "credentials.json",
    "mse802 quantum computing",
    "secrets.toml",
    "venv",
}

TEXT_SUFFIXES = {
    ".csv",
    ".ipynb",
    ".json",
    ".md",
    ".qasm",
    ".txt",
    ".xml",
}

PATTERNS = {
    "private key": re.compile(
        r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"
    ),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    "OpenAI-style key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "local Windows path": re.compile(r"\b[A-Za-z]:\\(?:Users|workshop)\\"),
    "local Unix home path": re.compile(r"(?:/Users/|/home/)[^/\s]+/"),
    "student placeholder": re.compile(r"\*\*Student:\*\*|_{8,}"),
}


def inspect_text(path: Path, text: str, findings: list[dict[str, str]]) -> None:
    relative = str(path.relative_to(SUBMISSION)).replace("\\", "/")
    for finding_type, pattern in PATTERNS.items():
        if pattern.search(text):
            findings.append({"type": finding_type, "path": relative})


def main() -> None:
    forbidden_items: list[str] = []
    findings: list[dict[str, str]] = []
    scanned_files = 0

    for path in sorted(SUBMISSION.rglob("*")):
        relative = str(path.relative_to(SUBMISSION)).replace("\\", "/")
        if path.is_symlink():
            forbidden_items.append(f"symbolic link: {relative}")
        if path.name.lower() in FORBIDDEN_NAMES or path.suffix.lower() in {
            ".key",
            ".pem",
            ".pfx",
            ".p12",
        }:
            forbidden_items.append(relative)
        if not path.is_file():
            continue

        scanned_files += 1
        suffix = path.suffix.lower()
        if suffix in TEXT_SUFFIXES:
            inspect_text(
                path,
                path.read_text(encoding="utf-8", errors="replace"),
                findings,
            )
        elif suffix == ".docx":
            with zipfile.ZipFile(path) as archive:
                office_text = "\n".join(
                    archive.read(name).decode("utf-8", errors="replace")
                    for name in archive.namelist()
                    if name.endswith(".xml")
                )
            inspect_text(path, office_text, findings)
        elif suffix == ".png":
            with Image.open(path) as image:
                metadata_text = "\n".join(
                    str(value) for value in image.info.values()
                )
            inspect_text(path, metadata_text, findings)

    passed = not forbidden_items and not findings
    result = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "scope": "submission/",
        "summary": {
            "status": "PASS" if passed else "FAIL",
            "scanned_files": scanned_files,
            "forbidden_items": len(forbidden_items),
            "sensitive_pattern_matches": len(findings),
        },
        "forbidden_items": forbidden_items,
        "findings": findings,
        "note": "Matched values are intentionally never recorded.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    print(
        f"Privacy audit: {result['summary']['status']} "
        f"({scanned_files} files; {len(forbidden_items)} forbidden items; "
        f"{len(findings)} sensitive-pattern matches)"
    )
    if not passed:
        for item in forbidden_items:
            print(f"FAIL  forbidden item: {item}")
        for item in findings:
            print(f"FAIL  {item['type']}: {item['path']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
