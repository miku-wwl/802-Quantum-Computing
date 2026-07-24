"""Local, reproducible components for Assessment 2 Task 4."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int_]


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
