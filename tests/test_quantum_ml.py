from __future__ import annotations

import numpy as np

from mse802.quantum_ml import (
    create_quantum_classifier_circuit,
    deterministic_split,
    exact_output_probability,
    generate_bar_stripe_data,
    generate_pairs,
    parameter_count,
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
