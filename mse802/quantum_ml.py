"""Local, reproducible components for Assessment 2 Task 4."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from time import perf_counter
from typing import Any, Literal

import numpy as np
from numpy.typing import NDArray
from qiskit import QuantumCircuit, qasm2
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

from .quokka import QuokkaClient


FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int_]
QuantumBackendName = Literal["exact", "aer", "quokka"]


@dataclass(frozen=True)
class ImageDataset:
    """Binary bar/stripe images and their class labels."""

    features: FloatArray
    labels: IntArray
    names: tuple[str, ...]
    side_length: int


@dataclass(frozen=True)
class DatasetSplit:
    """Deterministic view of the starter's train/test partition."""

    training: FloatArray
    training_labels: IntArray
    test: FloatArray
    test_labels: IntArray
    training_indices: IntArray
    test_indices: IntArray
    seed: int


@dataclass(frozen=True)
class QuantumExecution:
    """One model prediction with enough evidence to audit its backend."""

    backend: QuantumBackendName
    probability_one: float
    shots: int | None
    counts: dict[str, int]
    qasm: str | None
    raw_payload: dict[str, Any] | None = None


@dataclass(frozen=True)
class OptimizationRecord:
    """One auditable point in a quantum-model optimization trace."""

    iteration: int
    objective_mae: float
    elapsed_seconds: float
    step_size: float
    perturbation_size: float


@dataclass(frozen=True)
class OptimizationResult:
    """Final parameters and resource counts from tracked SPSA training."""

    initial_angles: FloatArray
    angles: FloatArray
    records: tuple[OptimizationRecord, ...]
    backend: QuantumBackendName
    shots: int
    objective_evaluations: int
    circuit_executions: int
    elapsed_seconds: float


def generate_binary_code(bit_length: int) -> FloatArray:
    """Return all binary words using the starter's least-significant-bit order."""

    if bit_length < 1:
        raise ValueError("bit_length must be positive")
    values = np.arange(2**bit_length, dtype=np.uint64)[:, None]
    bit_positions = np.arange(bit_length, dtype=np.uint64)[None, :]
    return ((values >> bit_positions) & 1).astype(float)


def generate_bar_stripe_data(side_length: int = 2) -> ImageDataset:
    """Reproduce the starter's non-uniform horizontal/vertical images."""

    if side_length < 2:
        raise ValueError("side_length must be at least two")

    binary_codes = generate_binary_code(side_length)
    stripes = np.repeat(binary_codes, side_length, axis=0).reshape(
        2**side_length,
        side_length * side_length,
    )
    bars = np.repeat(
        binary_codes.reshape(2**side_length * side_length, 1),
        side_length,
        axis=1,
    ).reshape(2**side_length, side_length * side_length)

    # Remove all-black and all-white images, as in the supplied notebook.
    non_uniform_stripes = stripes[1:-1]
    non_uniform_bars = bars[1:-1]
    features = np.vstack((non_uniform_stripes, non_uniform_bars)).astype(float)
    labels = np.concatenate(
        (
            np.zeros(len(non_uniform_stripes), dtype=int),
            np.ones(len(non_uniform_bars), dtype=int),
        )
    )
    names = tuple(
        [f"stripe_{index + 1}" for index in range(len(non_uniform_stripes))]
        + [f"bar_{index + 1}" for index in range(len(non_uniform_bars))]
    )
    return ImageDataset(
        features=features,
        labels=labels,
        names=names,
        side_length=side_length,
    )


def deterministic_split(
    features: FloatArray,
    labels: IntArray,
    *,
    training_fraction: float = 0.75,
    seed: int = 802,
) -> DatasetSplit:
    """Make the starter's random split repeatable without hidden global state."""

    if features.ndim != 2:
        raise ValueError("features must be a two-dimensional array")
    if labels.ndim != 1 or len(labels) != len(features):
        raise ValueError("labels must be one-dimensional and match features")
    if not 0 < training_fraction < 1:
        raise ValueError("training_fraction must be strictly between zero and one")

    training_count = int(len(features) * training_fraction)
    if training_count == 0 or training_count == len(features):
        raise ValueError("training_fraction produces an empty partition")

    generator = np.random.default_rng(seed)
    training_indices = generator.choice(
        len(features),
        training_count,
        replace=False,
    )
    test_indices = np.setdiff1d(np.arange(len(features)), training_indices)
    return DatasetSplit(
        training=features[training_indices],
        training_labels=labels[training_indices],
        test=features[test_indices],
        test_labels=labels[test_indices],
        training_indices=training_indices,
        test_indices=test_indices,
        seed=seed,
    )


def generate_pairs(qubit_count: int) -> tuple[tuple[int, int], ...]:
    """Return the starter's post-order recursive qubit-pair schedule."""

    if qubit_count < 2 or qubit_count & (qubit_count - 1):
        raise ValueError("qubit_count must be a power of two of at least two")

    pairs: list[tuple[int, int]] = []

    def visit(start: int, end: int) -> None:
        if start == end:
            return
        midpoint = (start + end - 1) // 2
        visit(start, midpoint)
        visit(midpoint + 1, end)
        pairs.append((midpoint, end))

    visit(0, qubit_count - 1)
    return tuple(pairs)


def parameter_count(qubit_count: int) -> int:
    """Return two RY angles for every edge of the recursive tree."""

    return 2 * len(generate_pairs(qubit_count))


def create_quantum_classifier_circuit(
    sample: FloatArray,
    angles: FloatArray,
    *,
    measure: bool = True,
) -> QuantumCircuit:
    """Build the starter's basis encoder and recursive RY–RY–CX model."""

    sample = np.asarray(sample, dtype=float)
    angles = np.asarray(angles, dtype=float)
    if sample.ndim != 1:
        raise ValueError("sample must be a one-dimensional pixel vector")
    if not np.all(np.isin(sample, (0.0, 1.0))):
        raise ValueError("sample pixels must be binary")

    pairs = generate_pairs(len(sample))
    expected_parameters = 2 * len(pairs)
    if angles.shape != (expected_parameters,):
        raise ValueError(f"angles must have shape ({expected_parameters},)")

    circuit = QuantumCircuit(len(sample), 1, name="bar_stripe_classifier")

    # This is the data-input location: one basis-encoding X per white pixel.
    for qubit, pixel in enumerate(sample):
        if pixel > 0.5:
            circuit.x(qubit)

    parameter_index = 0
    for first_qubit, second_qubit in pairs:
        circuit.ry(angles[parameter_index], first_qubit)
        circuit.ry(angles[parameter_index + 1], second_qubit)
        circuit.cx(first_qubit, second_qubit)
        parameter_index += 2

    if measure:
        circuit.measure(len(sample) - 1, 0)
    return circuit


def exact_output_probability(sample: FloatArray, angles: FloatArray) -> float:
    """Return ideal P(output=1) without shots or a remote backend."""

    circuit = create_quantum_classifier_circuit(sample, angles, measure=False)
    output_qubit = circuit.num_qubits - 1
    probabilities = Statevector.from_instruction(circuit).probabilities(
        qargs=[output_qubit]
    )
    return float(probabilities[1])


def quokka_qasm(circuit: QuantumCircuit) -> str:
    """Export the endpoint-compatible OpenQASM subset used by Quokka."""

    source = qasm2.dumps(circuit)
    lines = [
        line
        for line in source.splitlines()
        if not line.strip().startswith('include "qelib1.inc"')
    ]
    return "\n".join(lines).strip() + "\n"


def execute_quantum_classifier(
    sample: FloatArray,
    angles: FloatArray,
    *,
    backend: QuantumBackendName = "aer",
    shots: int = 100,
    seed: int = 802,
    quokka_client: QuokkaClient | None = None,
) -> QuantumExecution:
    """Execute one sample on an exact, Aer, or Quokka backend."""

    if backend == "exact":
        return QuantumExecution(
            backend="exact",
            probability_one=exact_output_probability(sample, angles),
            shots=None,
            counts={},
            qasm=None,
        )
    if shots <= 0:
        raise ValueError("shots must be positive")

    circuit = create_quantum_classifier_circuit(sample, angles)
    if backend == "aer":
        simulator = AerSimulator(seed_simulator=seed)
        result = simulator.run(circuit, shots=shots).result()
        counts = {
            str(key): int(value) for key, value in result.get_counts().items()
        }
        return QuantumExecution(
            backend="aer",
            probability_one=counts.get("1", 0) / shots,
            shots=shots,
            counts=counts,
            qasm=qasm2.dumps(circuit),
        )

    if backend == "quokka":
        if quokka_client is None:
            raise ValueError("quokka_client is required for the Quokka backend")
        source = quokka_qasm(circuit)
        payload = quokka_client.submit_qasm(source, shots=shots)
        values = quokka_client.register_values(payload, "c")
        counts = dict(Counter(str(value) for value in values))
        return QuantumExecution(
            backend="quokka",
            probability_one=float(np.mean(values)),
            shots=len(values),
            counts=counts,
            qasm=source,
            raw_payload=payload,
        )

    raise ValueError(f"unknown quantum backend: {backend!r}")


def quantum_predictions(
    features: FloatArray,
    angles: FloatArray,
    *,
    backend: QuantumBackendName = "aer",
    shots: int = 256,
    seed: int = 802,
    quokka_client: QuokkaClient | None = None,
) -> FloatArray:
    """Return P(output=1) for every sample using one selected backend."""

    features = np.asarray(features, dtype=float)
    if features.ndim != 2:
        raise ValueError("features must be a two-dimensional array")
    return np.asarray(
        [
            execute_quantum_classifier(
                sample,
                angles,
                backend=backend,
                shots=shots,
                seed=seed + sample_index,
                quokka_client=quokka_client,
            ).probability_one
            for sample_index, sample in enumerate(features)
        ],
        dtype=float,
    )


def quantum_mean_absolute_error(
    features: FloatArray,
    labels: IntArray,
    angles: FloatArray,
    *,
    backend: QuantumBackendName = "aer",
    shots: int = 256,
    seed: int = 802,
) -> float:
    """Evaluate the starter notebook's mean absolute-error objective."""

    labels = np.asarray(labels, dtype=int)
    if labels.ndim != 1 or len(labels) != len(features):
        raise ValueError("labels must be one-dimensional and match features")
    probabilities = quantum_predictions(
        features,
        angles,
        backend=backend,
        shots=shots,
        seed=seed,
    )
    return float(np.mean(np.abs(probabilities - labels)))


def optimize_quantum_classifier_spsa(
    features: FloatArray,
    labels: IntArray,
    initial_angles: FloatArray,
    *,
    iterations: int = 60,
    backend: QuantumBackendName = "aer",
    shots: int = 256,
    seed: int = 802,
    a: float = 0.8,
    c: float = 0.4,
    alpha: float = 0.602,
    gamma: float = 0.101,
) -> OptimizationResult:
    """Train with seeded SPSA while retaining metric, time, and resource data."""

    if backend == "quokka":
        raise ValueError("tracked training is limited to local exact or Aer backends")
    if iterations < 1:
        raise ValueError("iterations must be positive")
    if shots <= 0:
        raise ValueError("shots must be positive")
    if min(a, c, alpha, gamma) <= 0:
        raise ValueError("SPSA hyperparameters must be positive")

    features = np.asarray(features, dtype=float)
    labels = np.asarray(labels, dtype=int)
    angles = np.asarray(initial_angles, dtype=float).copy()
    if features.ndim != 2:
        raise ValueError("features must be a two-dimensional array")
    if labels.ndim != 1 or len(labels) != len(features):
        raise ValueError("labels must be one-dimensional and match features")
    expected_parameters = parameter_count(features.shape[1])
    if angles.shape != (expected_parameters,):
        raise ValueError(f"initial_angles must have shape ({expected_parameters},)")

    generator = np.random.default_rng(seed)
    started = perf_counter()
    objective_evaluations = 0

    def objective(candidate: FloatArray) -> float:
        nonlocal objective_evaluations
        objective_evaluations += 1
        return quantum_mean_absolute_error(
            features,
            labels,
            candidate,
            backend=backend,
            shots=shots,
            seed=seed,
        )

    initial_objective = objective(angles)
    records = [
        OptimizationRecord(
            iteration=0,
            objective_mae=initial_objective,
            elapsed_seconds=perf_counter() - started,
            step_size=0.0,
            perturbation_size=0.0,
        )
    ]

    for iteration in range(1, iterations + 1):
        step_size = a / iteration**alpha
        perturbation_size = c / iteration**gamma
        delta = generator.choice((-1.0, 1.0), size=len(angles))
        objective_plus = objective(angles + perturbation_size * delta)
        objective_minus = objective(angles - perturbation_size * delta)
        gradient = (
            (objective_plus - objective_minus)
            / (2.0 * perturbation_size)
            * delta
        )
        angles = angles - step_size * gradient
        # RY is 2π-periodic; wrapping avoids needlessly large parameters.
        angles = (angles + np.pi) % (2.0 * np.pi) - np.pi
        current_objective = objective(angles)
        records.append(
            OptimizationRecord(
                iteration=iteration,
                objective_mae=current_objective,
                elapsed_seconds=perf_counter() - started,
                step_size=step_size,
                perturbation_size=perturbation_size,
            )
        )

    elapsed_seconds = perf_counter() - started
    return OptimizationResult(
        initial_angles=np.asarray(initial_angles, dtype=float).copy(),
        angles=angles,
        records=tuple(records),
        backend=backend,
        shots=shots,
        objective_evaluations=objective_evaluations,
        circuit_executions=objective_evaluations * len(features),
        elapsed_seconds=elapsed_seconds,
    )
