from __future__ import annotations

from unittest.mock import Mock

import pytest

from mse802 import AssessmentConfig, QuokkaClient, QuokkaError, run_qasm_locally


BELL_QASM = """OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cx q[0],q[1];
measure q -> c;
"""


def test_config_builds_https_qasm_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("QUOKKA_BASE_URL", "https://example.invalid/")
    monkeypatch.setenv("QUOKKA_QASM_PATH", "qsim/qasm")
    config = AssessmentConfig.from_env()
    assert config.quokka_qasm_url == "https://example.invalid/qsim/qasm"


def test_local_qasm_bell_state_has_only_correlated_results() -> None:
    counts = run_qasm_locally(BELL_QASM, shots=256, seed=802)
    assert set(counts) <= {"00", "11"}
    assert sum(counts.values()) == 256


def test_quokka_client_validates_and_returns_payload() -> None:
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"result": {"c": [0, 1, 1, 0]}}
    session = Mock()
    session.post.return_value = response
    client = QuokkaClient(AssessmentConfig.from_env(), session=session)

    payload = client.submit_qasm(BELL_QASM, shots=4)

    assert client.register_values(payload, "c") == [0, 1, 1, 0]
    session.post.assert_called_once()


def test_quokka_client_rejects_invalid_payload() -> None:
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"unexpected": "shape"}
    session = Mock()
    session.post.return_value = response
    client = QuokkaClient(AssessmentConfig.from_env(), session=session)

    with pytest.raises(QuokkaError):
        client.submit_qasm(BELL_QASM)


def test_quokka_client_normalizes_nested_one_bit_registers() -> None:
    payload = {"result": {"c": [[0], [1], [1], [0]]}}
    assert QuokkaClient.register_values(payload, "c") == [0, 1, 1, 0]
