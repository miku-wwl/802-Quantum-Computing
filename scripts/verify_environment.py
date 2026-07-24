"""Verify the local software stack required by MSE802 Assessment 2."""

from __future__ import annotations

import importlib.metadata as metadata
import os
import sys

import cirq
from dotenv import load_dotenv
from qiskit import QuantumCircuit, qasm2
from qiskit_aer import AerSimulator


def check_python() -> None:
    if sys.version_info[:2] != (3, 11):
        raise RuntimeError(
            f"Expected Python 3.11, found {sys.version.split()[0]}. "
            "Run this script with 'uv run python scripts/verify_environment.py'."
        )


def check_cirq_bell_state() -> None:
    q0, q1 = cirq.LineQubit.range(2)
    circuit = cirq.Circuit(
        cirq.H(q0),
        cirq.CNOT(q0, q1),
        cirq.measure(q0, q1, key="result"),
    )
    result = cirq.Simulator(seed=802).run(circuit, repetitions=512)
    counts = result.histogram(key="result")
    if not counts or any(state not in (0, 3) for state in counts):
        raise RuntimeError(f"Unexpected Cirq Bell-state counts: {counts}")
    print(f"Cirq Bell-state simulation: PASS ({dict(counts)})")


def check_qiskit_and_qasm() -> None:
    circuit = QuantumCircuit(2, 2)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.measure([0, 1], [0, 1])

    qasm_source = qasm2.dumps(circuit)
    imported = qasm2.loads(qasm_source)
    result = AerSimulator(seed_simulator=802).run(imported, shots=512).result()
    counts = result.get_counts()
    if not counts or any(state not in ("00", "11") for state in counts):
        raise RuntimeError(f"Unexpected Qiskit Bell-state counts: {counts}")
    print(f"Qiskit Aer and OpenQASM 2 round trip: PASS ({counts})")


def print_versions() -> None:
    packages = (
        "cirq",
        "qiskit",
        "qiskit-aer",
        "qiskit-machine-learning",
        "jupyterlab",
        "numpy",
        "scipy",
        "scikit-learn",
        "matplotlib",
    )
    print(f"Python: {sys.version.split()[0]}")
    for package in packages:
        print(f"{package}: {metadata.version(package)}")


def report_quokka_configuration() -> None:
    base_url = os.getenv("QUOKKA_BASE_URL")
    if base_url:
        print(
            "Quokka endpoint configuration: PRESENT "
            "(this script does not submit or test a remote job)"
        )
    else:
        print(
            "Quokka endpoint configuration: NOT SET "
            "(local simulation works; physical/remote Quokka execution needs "
            "the endpoint supplied by the tutor or device administrator)"
        )


def main() -> None:
    load_dotenv()
    check_python()
    print_versions()
    check_cirq_bell_state()
    check_qiskit_and_qasm()
    report_quokka_configuration()
    print("Local MSE802 base environment: PASS")


if __name__ == "__main__":
    main()
