from __future__ import annotations

import numpy as np

from mse802.quantum_ml import (
    create_quantum_classifier_circuit,
    deterministic_split,
    exact_output_probability,
    execute_quantum_classifier,
    generate_bar_stripe_data,
    generate_pairs,
    optimize_quantum_classifier_spsa,
    parameter_count,
    quantum_mean_absolute_error,
    quokka_qasm,
)


def test_task4_dataset_matches_the_starter() -> None:
    data = generate_bar_stripe_data(side_length=2)

    assert data.features.tolist() == [
        [1.0, 0.0, 1.0, 0.0],
        [0.0, 1.0, 0.0, 1.0],
        [1.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 1.0],
    ]
    assert data.labels.tolist() == [0, 0, 1, 1]


def test_task4_split_is_reproducible_and_contains_both_training_classes() -> None:
    data = generate_bar_stripe_data()
    first = deterministic_split(data.features, data.labels, seed=802)
    second = deterministic_split(data.features, data.labels, seed=802)

    assert first.training_indices.tolist() == [3, 0, 2]
    assert first.test_indices.tolist() == [1]
    assert np.array_equal(first.training_indices, second.training_indices)
    assert set(first.training_labels) == {0, 1}


def test_recursive_pair_schedule_and_parameter_count() -> None:
    assert generate_pairs(4) == ((0, 1), (2, 3), (1, 3))
    assert parameter_count(4) == 6


def test_circuit_contains_basis_input_model_blocks_and_output_measurement() -> None:
    sample = np.array([1.0, 0.0, 1.0, 0.0])
    circuit = create_quantum_classifier_circuit(sample, np.zeros(6))

    assert circuit.num_qubits == 4
    assert circuit.num_clbits == 1
    assert circuit.count_ops() == {"ry": 6, "cx": 3, "x": 2, "measure": 1}
    measurement = circuit.data[-1]
    assert measurement.operation.name == "measure"
    assert circuit.find_bit(measurement.qubits[0]).index == 3
    assert circuit.find_bit(measurement.clbits[0]).index == 0


def test_zero_angles_compute_even_parity_for_the_four_images() -> None:
    data = generate_bar_stripe_data()
    predictions = [
        exact_output_probability(sample, np.zeros(6)) for sample in data.features
    ]
    assert np.allclose(predictions, 0.0, atol=1e-12)


def test_exact_and_aer_backends_share_the_same_circuit_semantics() -> None:
    sample = np.array([1.0, 0.0, 1.0, 0.0])
    angles = np.array([0.2, -0.4, 0.6, 0.8, -0.3, 0.5])
    exact = execute_quantum_classifier(sample, angles, backend="exact")
    aer = execute_quantum_classifier(
        sample,
        angles,
        backend="aer",
        shots=10_000,
        seed=802,
    )

    assert exact.shots is None
    assert aer.shots == 10_000
    assert abs(aer.probability_one - exact.probability_one) < 0.025


def test_quokka_export_removes_only_the_library_include() -> None:
    circuit = create_quantum_classifier_circuit(
        np.array([1.0, 0.0, 1.0, 0.0]),
        np.zeros(6),
    )
    source = quokka_qasm(circuit)

    assert source.startswith("OPENQASM 2.0;")
    assert "qelib1.inc" not in source
    assert "measure q[3] -> c[0];" in source


def test_quokka_backend_normalizes_nested_one_bit_results() -> None:
    class FakeQuokkaClient:
        def submit_qasm(self, source, shots):
            assert "qelib1.inc" not in source
            assert shots == 4
            return {"result": {"c": [[0], [1], [1], [0]]}}

        @staticmethod
        def register_values(payload, register):
            assert register == "c"
            return [value[0] for value in payload["result"][register]]

    result = execute_quantum_classifier(
        np.array([1.0, 0.0, 1.0, 0.0]),
        np.zeros(6),
        backend="quokka",
        shots=4,
        quokka_client=FakeQuokkaClient(),
    )

    assert result.probability_one == 0.5
    assert result.counts == {"0": 2, "1": 2}


def test_quantum_objective_is_starter_mean_absolute_error() -> None:
    data = generate_bar_stripe_data()
    angles = np.array([0.2, -0.4, 0.6, 0.8, -0.3, 0.5])
    probabilities = np.array(
        [exact_output_probability(sample, angles) for sample in data.features]
    )

    objective = quantum_mean_absolute_error(
        data.features,
        data.labels,
        angles,
        backend="exact",
    )

    assert np.isclose(objective, np.mean(np.abs(probabilities - data.labels)))


def test_tracked_spsa_is_reproducible_and_counts_resources() -> None:
    data = generate_bar_stripe_data()
    split = deterministic_split(data.features, data.labels, seed=802)
    initial_angles = np.linspace(-0.5, 0.5, 6)
    first = optimize_quantum_classifier_spsa(
        split.training,
        split.training_labels,
        initial_angles,
        iterations=2,
        backend="aer",
        shots=64,
        seed=802,
    )
    second = optimize_quantum_classifier_spsa(
        split.training,
        split.training_labels,
        initial_angles,
        iterations=2,
        backend="aer",
        shots=64,
        seed=802,
    )

    assert len(first.records) == 3
    assert [record.iteration for record in first.records] == [0, 1, 2]
    assert all(
        later.elapsed_seconds >= earlier.elapsed_seconds
        for earlier, later in zip(first.records, first.records[1:])
    )
    assert first.objective_evaluations == 7
    assert first.circuit_executions == 21
    assert np.allclose(first.angles, second.angles)
    assert np.allclose(
        [record.objective_mae for record in first.records],
        [record.objective_mae for record in second.records],
    )
