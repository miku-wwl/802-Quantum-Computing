from pathlib import Path

import numpy as np

from mse802.classical_ml import (
    fit_classical_orientation_classifier,
    orientation_features,
    predict_classical_orientation_classifier,
)
from mse802.quantum_ml import deterministic_split, generate_bar_stripe_data


def test_orientation_features_separate_stripes_and_bars() -> None:
    data = generate_bar_stripe_data()

    features = orientation_features(data.features)

    assert np.allclose(
        features,
        np.array(
            [
                [0.0, 1.0],
                [0.0, 1.0],
                [1.0, 0.0],
                [1.0, 0.0],
            ]
        ),
    )


def test_classical_model_generalizes_to_the_held_out_stripe() -> None:
    data = generate_bar_stripe_data()
    split = deterministic_split(data.features, data.labels, seed=802)

    fitted = fit_classical_orientation_classifier(
        split.training,
        split.training_labels,
    )
    prediction = predict_classical_orientation_classifier(fitted, data.features)

    assert prediction.labels.tolist() == data.labels.tolist()
    assert np.all(
        (prediction.probability_one >= 0.0)
        & (prediction.probability_one <= 1.0)
    )
    assert fitted.fit_seconds >= 0.0
    assert prediction.predict_seconds >= 0.0


def test_classical_module_has_no_quantum_dependency() -> None:
    source = (
        Path(__file__).parents[1] / "mse802" / "classical_ml.py"
    ).read_text(encoding="utf-8")
    lowered = source.lower()

    assert "qiskit" not in lowered
    assert "quantumcircuit" not in lowered
    assert "quokkaclient" not in lowered
    assert "qasm2" not in lowered
