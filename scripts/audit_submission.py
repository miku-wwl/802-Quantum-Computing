"""Audit the MSE802 Assessment 2 submission folder.

The script checks the final deliverables without contacting any remote backend.
It writes a machine-readable report and exits non-zero if any check fails.
"""

from __future__ import annotations

import json
import sys
import zipfile
from datetime import UTC, datetime
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SUBMISSION = ROOT / "submission"
OUTPUT = SUBMISSION / "SUBMISSION_AUDIT.json"

TASKS = {
    "Task 1": SUBMISSION / "Task_1_Entanglement",
    "Task 2": SUBMISSION / "Task_2_Qiskit",
    "Task 3": SUBMISSION / "Task_3_Quantum_Tic_Tac_Toe",
    "Task 4": SUBMISSION / "Task_4_Quantum_ML",
}

REQUIRED_FILES = {
    "Task 1": (
        "Task_1_Entanglement.ipynb",
        "task1_bell_quokka.qasm",
        "task1_local_histogram.png",
        "task1_quokka_histogram.png",
        "task1_quokka_metadata.json",
        "task1_quokka_raw.json",
    ),
    "Task 2": (
        "Task_2_Qiskit.ipynb",
        "task2_specified_standard.qasm",
        "task2_specified_quokka.qasm",
        "task2_custom_standard.qasm",
        "task2_custom_quokka.qasm",
        "task2_aer_quokka_comparison.png",
        "task2_specified_quokka_raw.json",
        "task2_custom_quokka_raw.json",
    ),
    "Task 3": (
        "Task_3_Quantum_Tic_Tac_Toe.ipynb",
        "Task_3_Quantum_Tic_Tac_Toe_Report.docx",
        "task3_game_evidence.json",
        "task3_four_game_summary.png",
        "game_1_rows.qasm",
        "game_2_not.qasm",
        "game_3_swap.qasm",
        "game_4_open.qasm",
    ),
    "Task 4": (
        "Task_4_Quantum_ML.ipynb",
        "Task_4_Quantum_ML_Report.docx",
        "task4_backend_validation.json",
        "task4_circuit_analysis.json",
        "task4_quantum_optimization.json",
        "task4_quantum_optimization_trace.csv",
        "task4_classical_baseline.json",
        "task4_quantum_classical_benchmark.json",
        "task4_quantum_classical_benchmark.csv",
        "task4_quantum_classical_comparison.png",
    ),
}


class Audit:
    """Collect pass/fail checks and serialize their evidence."""

    def __init__(self) -> None:
        self.checks: list[dict[str, str]] = []

    def check(self, name: str, condition: bool, detail: str) -> None:
        self.checks.append(
            {
                "name": name,
                "status": "PASS" if condition else "FAIL",
                "detail": detail,
            }
        )

    @property
    def passed(self) -> bool:
        return all(item["status"] == "PASS" for item in self.checks)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def audit_required_files(audit: Audit) -> None:
    for task, directory in TASKS.items():
        missing = [
            name for name in REQUIRED_FILES[task] if not (directory / name).is_file()
        ]
        audit.check(
            f"{task} required files",
            not missing,
            "all required files present" if not missing else f"missing: {missing}",
        )


def audit_notebooks(audit: Audit) -> None:
    for task, directory in TASKS.items():
        notebooks = sorted(directory.glob("*.ipynb"))
        if len(notebooks) != 1:
            audit.check(
                f"{task} notebook",
                False,
                f"expected one notebook, found {len(notebooks)}",
            )
            continue

        notebook = read_json(notebooks[0])
        cells = notebook.get("cells", [])
        code_cells = [cell for cell in cells if cell.get("cell_type") == "code"]
        markdown = "\n".join(
            "".join(cell.get("source", ""))
            for cell in cells
            if cell.get("cell_type") == "markdown"
        )
        errors = [
            output
            for cell in code_cells
            for output in cell.get("outputs", [])
            if output.get("output_type") == "error"
        ]
        unexecuted = [
            index
            for index, cell in enumerate(cells)
            if cell.get("cell_type") == "code"
            and cell.get("execution_count") is None
        ]
        valid = (
            notebook.get("nbformat") == 4
            and bool(code_cells)
            and not errors
            and not unexecuted
            and "## References" in markdown
            and "**Course:** MSE802 Quantum Computing" in markdown
            and "**Student:**" not in markdown
            and "________" not in markdown
        )
        audit.check(
            f"{task} clean notebook execution",
            valid,
            (
                f"{len(code_cells)} code cells executed; no errors; references and "
                "course metadata present"
                if valid
                else (
                    f"errors={len(errors)}, unexecuted={unexecuted}, "
                    "metadata/references incomplete"
                )
            ),
        )


def audit_file_formats(audit: Audit) -> None:
    qasm_files = sorted(SUBMISSION.rglob("*.qasm"))
    bad_qasm = [
        str(path.relative_to(SUBMISSION))
        for path in qasm_files
        if "OPENQASM 2.0;" not in path.read_text(encoding="utf-8")
    ]
    audit.check(
        "OpenQASM evidence",
        len(qasm_files) >= 10 and not bad_qasm,
        f"{len(qasm_files)} OpenQASM 2 files validated"
        if not bad_qasm
        else f"invalid files: {bad_qasm}",
    )

    image_files = sorted(SUBMISSION.rglob("*.png"))
    bad_images: list[str] = []
    for path in image_files:
        try:
            with Image.open(path) as image:
                image.verify()
        except Exception:
            bad_images.append(str(path.relative_to(SUBMISSION)))
    audit.check(
        "PNG figures",
        len(image_files) >= 17 and not bad_images,
        f"{len(image_files)} PNG files decoded successfully"
        if not bad_images
        else f"invalid files: {bad_images}",
    )

    reports = sorted(SUBMISSION.rglob("*.docx"))
    bad_reports = [
        str(path.relative_to(SUBMISSION))
        for path in reports
        if not zipfile.is_zipfile(path)
    ]
    audit.check(
        "Word reports",
        len(reports) == 2 and not bad_reports,
        "Task 3 and Task 4 DOCX packages are readable"
        if not bad_reports
        else f"invalid files: {bad_reports}",
    )

    json_files = sorted(SUBMISSION.rglob("*.json"))
    bad_json: list[str] = []
    for path in json_files:
        try:
            read_json(path)
        except (OSError, json.JSONDecodeError):
            bad_json.append(str(path.relative_to(SUBMISSION)))
    audit.check(
        "JSON evidence",
        len(json_files) >= 12 and not bad_json,
        f"{len(json_files)} JSON files parsed successfully"
        if not bad_json
        else f"invalid files: {bad_json}",
    )


def audit_evidence_content(audit: Audit) -> None:
    task1 = read_json(TASKS["Task 1"] / "task1_quokka_metadata.json")
    audit.check(
        "Task 1 Quokka provenance",
        task1.get("shots_requested") == 1024
        and str(task1.get("endpoint", "")).startswith("https://")
        and bool(task1.get("captured_at_utc")),
        "HTTPS endpoint, UTC timestamp, and 1024-shot request retained",
    )

    task2_metadata = [
        read_json(TASKS["Task 2"] / name)
        for name in (
            "task2_specified_quokka_metadata.json",
            "task2_custom_quokka_metadata.json",
        )
    ]
    audit.check(
        "Task 2 Quokka provenance",
        all(
            item.get("shots_requested") == 1024
            and str(item.get("endpoint", "")).startswith("https://")
            and item.get("captured_at_utc")
            for item in task2_metadata
        ),
        "both 1024-shot runs retain HTTPS endpoints and UTC timestamps",
    )

    task3 = read_json(TASKS["Task 3"] / "task3_game_evidence.json")
    games = task3.get("games", [])
    audit.check(
        "Task 3 game evidence",
        len(games) == 4
        and all(
            game.get("seed") is not None and game.get("result") for game in games
        ),
        "four games retain seeds, move histories, measurements, and scores",
    )

    task4_backend = read_json(
        TASKS["Task 4"] / "task4_backend_validation.json"
    )
    task4_benchmark = read_json(
        TASKS["Task 4"] / "task4_quantum_classical_benchmark.json"
    )
    audit.check(
        "Task 4 backend and benchmark evidence",
        len(task4_backend.get("records", [])) == 4
        and task4_benchmark["quantum"]["metrics"]["full"]["accuracy"] == 1.0
        and task4_benchmark["classical"]["metrics"]["full"]["accuracy"] == 1.0
        and task4_benchmark["classical"]["efficiency"][
            "quantum_circuit_executions"
        ]
        == 0,
        "four backend samples; quantum/classical metrics and no-circuit baseline retained",
    )


def main() -> None:
    audit = Audit()
    audit.check(
        "Submission task folders",
        all(directory.is_dir() for directory in TASKS.values()),
        "four distinct task folders present",
    )
    audit_required_files(audit)
    audit_notebooks(audit)
    audit_file_formats(audit)
    audit_evidence_content(audit)

    passed_count = sum(item["status"] == "PASS" for item in audit.checks)
    result = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "scope": "MSE802 Assessment 2 final submission",
        "remote_requests_made": 0,
        "summary": {
            "status": "PASS" if audit.passed else "FAIL",
            "passed": passed_count,
            "total": len(audit.checks),
        },
        "checks": audit.checks,
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    for item in audit.checks:
        print(f"{item['status']:4}  {item['name']}: {item['detail']}")
    print(f"Submission audit: {result['summary']['status']} ({passed_count}/{len(audit.checks)})")

    if not audit.passed:
        sys.exit(1)


if __name__ == "__main__":
    main()
