"""Backend-neutral metrics used by the Task 4 comparison."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int_]


@dataclass(frozen=True)
class BinaryMetrics:
    """Threshold accuracy and probability-sensitive mean absolute error."""

    accuracy: float
    mean_absolute_error: float
    predicted_labels: IntArray


def binary_metrics(
    labels: IntArray,
    probability_one: FloatArray,
    *,
    threshold: float = 0.5,
) -> BinaryMetrics:
    """Compute the common effectiveness measures for both Task 4 models."""

    labels = np.asarray(labels, dtype=int)
    probability_one = np.asarray(probability_one, dtype=float)
    if labels.ndim != 1 or probability_one.ndim != 1:
        raise ValueError("labels and probability_one must be one-dimensional")
    if labels.shape != probability_one.shape:
        raise ValueError("labels and probability_one must have the same shape")
    if not np.all(np.isin(labels, (0, 1))):
        raise ValueError("labels must be binary")
    if not np.all((probability_one >= 0.0) & (probability_one <= 1.0)):
        raise ValueError("probabilities must be between zero and one")
    if not 0.0 < threshold < 1.0:
        raise ValueError("threshold must be strictly between zero and one")

    predicted_labels = (probability_one >= threshold).astype(int)
    return BinaryMetrics(
        accuracy=float(np.mean(predicted_labels == labels)),
        mean_absolute_error=float(np.mean(np.abs(probability_one - labels))),
        predicted_labels=predicted_labels,
    )
