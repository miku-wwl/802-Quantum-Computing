"""Local simulation helpers that mirror the Quokka OpenQASM workflow."""

from __future__ import annotations

from qiskit import qasm2
from qiskit_aer import AerSimulator


def run_qasm_locally(
    qasm_source: str, *, shots: int = 1024, seed: int = 802
) -> dict[str, int]:
    """Parse OpenQASM 2, run it with Aer, and return measurement counts."""

    if shots <= 0:
        raise ValueError("shots must be positive")
    circuit = qasm2.loads(qasm_source)
    backend = AerSimulator(seed_simulator=seed)
    result = backend.run(circuit, shots=shots).result()
    return {str(key): int(value) for key, value in result.get_counts().items()}
