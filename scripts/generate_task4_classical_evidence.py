"""Run and retain the fully classical Task 4 no-circuit baseline."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "submission" / "Task_4_Quantum_ML"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mse802.classical_ml import (
    fit_classical_orientation_classifier,
    orientation_features,
    predict_classical_orientation_classifier,
)
from mse802.quantum_ml import deterministic_split, generate_bar_stripe_data


SEED = 802


def accuracy(actual: np.ndarray, predicted: np.ndarray) -> float:
    return float(np.mean(actual == predicted))


def mean_absolute_error(actual: np.ndarray, probability_one: np.ndarray) -> float:
    return float(np.mean(np.abs(probability_one - actual)))


def main() -> None:
    data = generate_bar_stripe_data()
    split = deterministic_split(data.features, data.labels, seed=SEED)
    fitted = fit_classical_orientation_classifier(
        split.training,
        split.training_labels,
        side_length=data.side_length,
    )
    training_prediction = predict_classical_orientation_classifier(
        fitted,
        split.training,
    )
    test_prediction = predict_classical_orientation_classifier(fitted, split.test)
    full_prediction = predict_classical_orientation_classifier(fitted, data.features)

    evidence = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "implementation": "classical orientation features plus logistic regression",
        "quantum_circuits": 0,
        "quantum_shots": 0,
        "quantum_backend": None,
        "seed": SEED,
        "feature_names": ["vertical_change", "horizontal_change"],
        "all_orientation_features": orientation_features(data.features).tolist(),
        "training_indices": split.training_indices.tolist(),
        "test_indices": split.test_indices.tolist(),
        "model": {
            "type": "sklearn.linear_model.LogisticRegression",
            "C": 100.0,
            "class_weight": "balanced",
            "coefficient": fitted.estimator.coef_[0].tolist(),
            "intercept": fitted.estimator.intercept_.tolist(),
        },
        "fit_seconds": fitted.fit_seconds,
        "training_predict_seconds": training_prediction.predict_seconds,
        "test_predict_seconds": test_prediction.predict_seconds,
        "full_predict_seconds": full_prediction.predict_seconds,
        "training": {
            "labels": split.training_labels.tolist(),
            "probability_one": training_prediction.probability_one.tolist(),
            "predicted_labels": training_prediction.labels.tolist(),
            "accuracy": accuracy(
                split.training_labels,
                training_prediction.labels,
            ),
            "mean_absolute_error": mean_absolute_error(
                split.training_labels,
                training_prediction.probability_one,
            ),
        },
        "test": {
            "labels": split.test_labels.tolist(),
            "probability_one": test_prediction.probability_one.tolist(),
            "predicted_labels": test_prediction.labels.tolist(),
            "accuracy": accuracy(split.test_labels, test_prediction.labels),
            "mean_absolute_error": mean_absolute_error(
                split.test_labels,
                test_prediction.probability_one,
            ),
        },
        "full_dataset": {
            "labels": data.labels.tolist(),
            "probability_one": full_prediction.probability_one.tolist(),
            "predicted_labels": full_prediction.labels.tolist(),
            "accuracy": accuracy(data.labels, full_prediction.labels),
            "mean_absolute_error": mean_absolute_error(
                data.labels,
                full_prediction.probability_one,
            ),
        },
        "scope_note": (
            "This module imports NumPy and scikit-learn only. It does not create "
            "QASM, a quantum circuit, simulator jobs, remote requests, or shots."
        ),
    }
    (OUTPUT / "task4_classical_baseline.json").write_text(
        json.dumps(evidence, indent=2),
        encoding="utf-8",
    )
    print(
        f"training accuracy={evidence['training']['accuracy']:.3f}; "
        f"test accuracy={evidence['test']['accuracy']:.3f}; "
        f"full accuracy={evidence['full_dataset']['accuracy']:.3f}"
    )
    print(
        f"fit={fitted.fit_seconds:.6f}s; "
        f"full prediction={full_prediction.predict_seconds:.6f}s"
    )


if __name__ == "__main__":
    main()
