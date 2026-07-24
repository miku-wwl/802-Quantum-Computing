"""Benchmark Task 4 quantum and classical implementations on the same split."""

from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from time import perf_counter

import matplotlib
import numpy as np


matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "submission" / "Task_4_Quantum_ML"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mse802.classical_ml import (
    fit_classical_orientation_classifier,
    predict_classical_orientation_classifier,
)
from mse802.evaluation import BinaryMetrics, binary_metrics
from mse802.quantum_ml import (
    deterministic_split,
    generate_bar_stripe_data,
    quantum_predictions,
)


SEED = 802
SHOTS = 256
TIMING_REPETITIONS = 7


def metric_dict(metrics: BinaryMetrics) -> dict[str, object]:
    return {
        "accuracy": metrics.accuracy,
        "mean_absolute_error": metrics.mean_absolute_error,
        "predicted_labels": metrics.predicted_labels.tolist(),
    }


def measured_call(callable_):
    started = perf_counter()
    value = callable_()
    return value, perf_counter() - started


def add_value_labels(axis, bars, *, digits: int) -> None:
    for bar in bars:
        value = bar.get_height()
        axis.annotate(
            f"{value:.{digits}f}",
            xy=(bar.get_x() + bar.get_width() / 2, value),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8,
        )


def save_comparison_figure(rows: list[dict[str, object]]) -> None:
    quantum = next(row for row in rows if row["model"] == "quantum")
    classical = next(row for row in rows if row["model"] == "classical")
    colors = ["#0B7285", "#D97706"]
    figure, axes = plt.subplots(2, 2, figsize=(9.2, 7.0))

    scopes = ["training", "test", "full"]
    x = np.arange(len(scopes))
    width = 0.36
    for axis, metric, title, ylabel in (
        (axes[0, 0], "accuracy", "Effectiveness: accuracy", "Accuracy"),
        (
            axes[0, 1],
            "mean_absolute_error",
            "Effectiveness: probability MAE",
            "Mean absolute error",
        ),
    ):
        quantum_values = [quantum[f"{scope}_{metric}"] for scope in scopes]
        classical_values = [classical[f"{scope}_{metric}"] for scope in scopes]
        first = axis.bar(
            x - width / 2,
            quantum_values,
            width,
            label="Quantum",
            color=colors[0],
        )
        second = axis.bar(
            x + width / 2,
            classical_values,
            width,
            label="Classical",
            color=colors[1],
        )
        axis.set_xticks(x, ["Training", "Test", "Full"])
        axis.set_ylabel(ylabel)
        axis.set_title(title)
        axis.grid(axis="y", alpha=0.25)
        axis.legend()
        add_value_labels(axis, first, digits=3)
        add_value_labels(axis, second, digits=3)

    training_bars = axes[1, 0].bar(
        ["Quantum", "Classical"],
        [quantum["training_seconds"], classical["training_seconds"]],
        color=colors,
    )
    axes[1, 0].set_yscale("log")
    axes[1, 0].set_ylabel("Seconds (log scale)")
    axes[1, 0].set_title("Efficiency: model training")
    axes[1, 0].grid(axis="y", alpha=0.25)
    add_value_labels(axes[1, 0], training_bars, digits=4)

    inference_bars = axes[1, 1].bar(
        ["Quantum", "Classical"],
        [
            quantum["full_inference_median_seconds"],
            classical["full_inference_median_seconds"],
        ],
        color=colors,
    )
    axes[1, 1].set_yscale("log")
    axes[1, 1].set_ylabel("Seconds (log scale)")
    axes[1, 1].set_title("Efficiency: four-sample inference")
    axes[1, 1].grid(axis="y", alpha=0.25)
    add_value_labels(axes[1, 1], inference_bars, digits=5)

    figure.suptitle("Task 4 quantum/classical benchmark", fontsize=15)
    figure.tight_layout()
    figure.savefig(OUTPUT / "task4_quantum_classical_comparison.png", dpi=180)
    plt.close(figure)


def main() -> None:
    data = generate_bar_stripe_data()
    split = deterministic_split(data.features, data.labels, seed=SEED)
    optimization = json.loads(
        (OUTPUT / "task4_quantum_optimization.json").read_text(encoding="utf-8")
    )
    optimized_angles = np.asarray(optimization["optimized_angles"], dtype=float)

    # Warm both paths before timing to reduce one-off import/allocation effects.
    quantum_predictions(
        data.features,
        optimized_angles,
        backend="aer",
        shots=SHOTS,
        seed=SEED,
    )
    classical_fit = fit_classical_orientation_classifier(
        split.training,
        split.training_labels,
        side_length=data.side_length,
    )
    predict_classical_orientation_classifier(classical_fit, data.features)

    quantum_times: list[float] = []
    classical_times: list[float] = []
    quantum_full = np.empty(len(data.features))
    classical_full = None
    for _ in range(TIMING_REPETITIONS):
        quantum_full, quantum_seconds = measured_call(
            lambda: quantum_predictions(
                data.features,
                optimized_angles,
                backend="aer",
                shots=SHOTS,
                seed=SEED,
            )
        )
        classical_full, classical_seconds = measured_call(
            lambda: predict_classical_orientation_classifier(
                classical_fit,
                data.features,
            )
        )
        quantum_times.append(quantum_seconds)
        classical_times.append(classical_seconds)

    quantum_training = quantum_predictions(
        split.training,
        optimized_angles,
        backend="aer",
        shots=SHOTS,
        seed=SEED,
    )
    quantum_test = quantum_predictions(
        split.test,
        optimized_angles,
        backend="aer",
        shots=SHOTS,
        seed=SEED,
    )
    classical_training = predict_classical_orientation_classifier(
        classical_fit,
        split.training,
    )
    classical_test = predict_classical_orientation_classifier(
        classical_fit,
        split.test,
    )
    assert classical_full is not None

    quantum_metrics = {
        "training": binary_metrics(split.training_labels, quantum_training),
        "test": binary_metrics(split.test_labels, quantum_test),
        "full": binary_metrics(data.labels, quantum_full),
    }
    classical_metrics = {
        "training": binary_metrics(
            split.training_labels,
            classical_training.probability_one,
        ),
        "test": binary_metrics(
            split.test_labels,
            classical_test.probability_one,
        ),
        "full": binary_metrics(data.labels, classical_full.probability_one),
    }

    rows: list[dict[str, object]] = []
    for model, metrics, training_seconds, inference_seconds in (
        (
            "quantum",
            quantum_metrics,
            optimization["elapsed_seconds"],
            median(quantum_times),
        ),
        (
            "classical",
            classical_metrics,
            classical_fit.fit_seconds,
            median(classical_times),
        ),
    ):
        row: dict[str, object] = {
            "model": model,
            "training_seconds": training_seconds,
            "full_inference_median_seconds": inference_seconds,
        }
        for scope in ("training", "test", "full"):
            row[f"{scope}_accuracy"] = metrics[scope].accuracy
            row[f"{scope}_mean_absolute_error"] = (
                metrics[scope].mean_absolute_error
            )
        rows.append(row)

    with (OUTPUT / "task4_quantum_classical_benchmark.csv").open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    save_comparison_figure(rows)

    evidence = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "comparison_protocol": {
            "split_seed": SEED,
            "training_indices": split.training_indices.tolist(),
            "test_indices": split.test_indices.tolist(),
            "classification_threshold": 0.5,
            "quantum_backend": "local Aer",
            "shots_per_quantum_circuit": SHOTS,
            "timing_repetitions": TIMING_REPETITIONS,
            "timing_statistic": "median wall-clock seconds",
        },
        "quantum": {
            "probability_one": {
                "training": quantum_training.tolist(),
                "test": quantum_test.tolist(),
                "full": quantum_full.tolist(),
            },
            "metrics": {
                scope: metric_dict(metrics)
                for scope, metrics in quantum_metrics.items()
            },
            "efficiency": {
                "training_seconds": optimization["elapsed_seconds"],
                "training_objective_evaluations": optimization[
                    "objective_evaluations"
                ],
                "training_circuit_executions": optimization["circuit_executions"],
                "training_total_shots": optimization["total_shots"],
                "full_inference_median_seconds": median(quantum_times),
                "full_inference_seconds_all_repetitions": quantum_times,
                "circuits_per_full_inference": len(data.features),
                "shots_per_full_inference": len(data.features) * SHOTS,
            },
        },
        "classical": {
            "probability_one": {
                "training": classical_training.probability_one.tolist(),
                "test": classical_test.probability_one.tolist(),
                "full": classical_full.probability_one.tolist(),
            },
            "metrics": {
                scope: metric_dict(metrics)
                for scope, metrics in classical_metrics.items()
            },
            "efficiency": {
                "training_seconds": classical_fit.fit_seconds,
                "full_inference_median_seconds": median(classical_times),
                "full_inference_seconds_all_repetitions": classical_times,
                "quantum_circuit_executions": 0,
                "quantum_shots": 0,
            },
        },
        "interpretation": {
            "accuracy": (
                "Both models classify all four supplied samples correctly at "
                "threshold 0.5, including the single held-out sample."
            ),
            "effectiveness": (
                "The classical model has lower probability MAE on this tiny, "
                "structurally simple dataset."
            ),
            "efficiency": (
                "The classical model is faster and uses no circuits or shots; "
                "the quantum training consumed 543 circuit executions and "
                "139008 shots."
            ),
            "limitation": (
                "There are only four samples and one test item. The engineered "
                "classical features match the data-generation rule, so these "
                "results do not establish generalisation or quantum advantage."
            ),
        },
    }
    (OUTPUT / "task4_quantum_classical_benchmark.json").write_text(
        json.dumps(evidence, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(evidence["interpretation"], indent=2))
    print(
        f"quantum/classical training-time ratio="
        f"{optimization['elapsed_seconds'] / classical_fit.fit_seconds:.1f}x"
    )


if __name__ == "__main__":
    main()
