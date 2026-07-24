import numpy as np
import pytest

from mse802.evaluation import binary_metrics


def test_binary_metrics_use_shared_probability_threshold() -> None:
    metrics = binary_metrics(
        np.array([0, 0, 1, 1]),
        np.array([0.1, 0.49, 0.5, 0.9]),
    )

    assert metrics.predicted_labels.tolist() == [0, 0, 1, 1]
    assert metrics.accuracy == 1.0
    assert np.isclose(metrics.mean_absolute_error, 0.2975)


def test_binary_metrics_reject_invalid_probabilities() -> None:
    with pytest.raises(ValueError, match="between zero and one"):
        binary_metrics(np.array([0, 1]), np.array([-0.1, 1.1]))
