from __future__ import annotations

import json
from pathlib import Path

from qiskit import qasm2

from mse802 import QuokkaClient


TASK_DIR = Path("submission/Task_1_Entanglement")


def test_task1_qasm_contains_required_bell_operations() -> None:
    qasm_source = (TASK_DIR / "task1_bell_quokka.qasm").read_text(encoding="utf-8")
    # The supplied Quokka workflow intentionally omits qelib1.inc. Restore the
    # declaration only for standards-based Qiskit parsing in this local test.
    parseable_source = qasm_source.replace(
        "OPENQASM 2.0;", 'OPENQASM 2.0;\ninclude "qelib1.inc";', 1
    )
    circuit = qasm2.loads(parseable_source)
    operation_names = [instruction.operation.name for instruction in circuit.data]
    assert operation_names[:2] == ["h", "cx"]
    assert operation_names.count("measure") == 2


def test_task1_quokka_evidence_is_complete_and_correlated() -> None:
    payload = json.loads(
        (TASK_DIR / "task1_quokka_raw.json").read_text(encoding="utf-8")
    )
    metadata = json.loads(
        (TASK_DIR / "task1_quokka_metadata.json").read_text(encoding="utf-8")
    )
    q0 = QuokkaClient.register_values(payload, "q0_out")
    q1 = QuokkaClient.register_values(payload, "q1_out")

    assert len(q0) == len(q1) == metadata["shots_requested"] == 1024
    assert all(bit0 == bit1 for bit0, bit1 in zip(q0, q1))
    assert payload["error_code"] == 0
