"""Fully classical Task 4 baseline with no quantum circuit dependency."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter

import numpy as np
from numpy.typing import NDArray
from sklearn.linear_model import LogisticRegression


FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int_]


@dataclass(frozen=True)
class ClassicalFit:
    """Fitted orientation classifier and measured local fit time."""

    estimator: LogisticRegression
    side_length: int
    fit_seconds: float


@dataclass(frozen=True)
class ClassicalPrediction:
    """Probabilities, thresholded labels, and local inference time."""

    probability_one: FloatArray
    labels: IntArray
    predict_seconds: float


def orientation_features(
    images: FloatArray,
    *,
    side_length: int = 2,
) -> FloatArray:
    """Map flattened images to vertical and horizontal change magnitudes."""

    images = np.asarray(images, dtype=float)
    if images.ndim != 2:
        raise ValueError("images must be a two-dimensional array")
    if side_length < 2 or images.shape[1] != side_length**2:
        raise ValueError("each row must contain one square flattened image")

    squares = images.reshape(-1, side_length, side_length)
    vertical_change = np.abs(np.diff(squares, axis=1)).mean(axis=(1, 2))
    horizontal_change = np.abs(np.diff(squares, axis=2)).mean(axis=(1, 2))
    return np.column_stack((vertical_change, horizontal_change))


def fit_classical_orientation_classifier(
    training_images: FloatArray,
    training_labels: IntArray,
    *,
    side_length: int = 2,
) -> ClassicalFit:
    """Fit balanced logistic regression on two classical image features."""

    training_labels = np.asarray(training_labels, dtype=int)
    if training_labels.ndim != 1 or len(training_labels) != len(training_images):
        raise ValueError("training_labels must match training_images")
    if len(np.unique(training_labels)) != 2:
        raise ValueError("training data must contain both classes")

    features = orientation_features(training_images, side_length=side_length)
    estimator = LogisticRegression(
        C=100.0,
        class_weight="balanced",
        solver="lbfgs",
        random_state=802,
    )
    started = perf_counter()
    estimator.fit(features, training_labels)
    fit_seconds = perf_counter() - started
    return ClassicalFit(
        estimator=estimator,
        side_length=side_length,
        fit_seconds=fit_seconds,
    )


def predict_classical_orientation_classifier(
    fitted: ClassicalFit,
    images: FloatArray,
) -> ClassicalPrediction:
    """Predict class 1 locally without constructing a quantum circuit."""

    features = orientation_features(images, side_length=fitted.side_length)
    started = perf_counter()
    probability_one = fitted.estimator.predict_proba(features)[:, 1]
    labels = fitted.estimator.predict(features).astype(int)
    predict_seconds = perf_counter() - started
    return ClassicalPrediction(
        probability_one=np.asarray(probability_one, dtype=float),
        labels=np.asarray(labels, dtype=int),
        predict_seconds=predict_seconds,
    )
