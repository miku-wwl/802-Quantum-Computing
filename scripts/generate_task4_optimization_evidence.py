"""Train the Task 4 quantum model and retain metric/time evidence."""

from __future__ import annotations

import csv
import json
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
import numpy as np


matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "submission" / "Task_4_Quantum_ML"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mse802.quantum_ml import (
    deterministic_split,
    generate_bar_stripe_data,
    optimize_quantum_classifier_spsa,
    quantum_predictions,
)


SEED = 802
SHOTS = 256
ITERATIONS = 60


def save_trace_plot(
    iterations: list[int],
    values: list[float],
    *,
    ylabel: str,
    title: str,
    filename: str,
    color: str,
) -> None:
    """Save one report-ready optimization trace plot."""

    figure, axis = plt.subplots(figsize=(7.2, 4.2))
    axis.plot(iterations, values, color=color, linewidth=2.0, marker="o", markersize=3)
    axis.set_xlabel("SPSA iteration")
    axis.set_ylabel(ylabel)
    axis.set_title(title)
    axis.grid(alpha=0.25)
    figure.tight_layout()
    figure.savefig(OUTPUT / filename, dpi=180)
    plt.close(figure)


def main() -> None:
    data = generate_bar_stripe_data()
    split = deterministic_split(data.features, data.labels, seed=SEED)
    generator = np.random.default_rng(SEED)
    initial_angles = np.pi * generator.standard_normal(6)
    result = optimize_quantum_classifier_spsa(
        split.training,
        split.training_labels,
        initial_angles,
        iterations=ITERATIONS,
        backend="aer",
        shots=SHOTS,
        seed=SEED,
    )

    trace_rows = [asdict(record) for record in result.records]
    with (OUTPUT / "task4_quantum_optimization_trace.csv").open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(trace_rows[0]))
        writer.writeheader()
        writer.writerows(trace_rows)

    iteration_values = [record.iteration for record in result.records]
    objective_values = [record.objective_mae for record in result.records]
    elapsed_values = [record.elapsed_seconds for record in result.records]
    save_trace_plot(
        iteration_values,
        objective_values,
        ylabel="Training mean absolute error",
        title="Quantum model objective by iteration",
        filename="task4_quantum_metric_by_iteration.png",
        color="#0B7285",
    )
    save_trace_plot(
        iteration_values,
        elapsed_values,
        ylabel="Cumulative elapsed time (seconds)",
        title="Quantum model cumulative training time",
        filename="task4_quantum_time_by_iteration.png",
        color="#D97706",
    )

    initial_probabilities = quantum_predictions(
        split.training,
        result.initial_angles,
        backend="aer",
        shots=SHOTS,
        seed=SEED,
    )
    final_training_probabilities = quantum_predictions(
        split.training,
        result.angles,
        backend="aer",
        shots=SHOTS,
        seed=SEED,
    )
    final_full_probabilities = quantum_predictions(
        data.features,
        result.angles,
        backend="aer",
        shots=SHOTS,
        seed=SEED,
    )
    evidence = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "backend": result.backend,
        "seed": SEED,
        "shots_per_circuit": SHOTS,
        "iterations": ITERATIONS,
        "optimizer": {
            "name": "seeded SPSA",
            "a": 0.8,
            "c": 0.4,
            "alpha": 0.602,
            "gamma": 0.101,
        },
        "objective": "mean(abs(P(output=1) - label)) over training samples",
        "training_indices": split.training_indices.tolist(),
        "test_indices": split.test_indices.tolist(),
        "initial_angles": result.initial_angles.tolist(),
        "optimized_angles": result.angles.tolist(),
        "initial_training_probabilities": initial_probabilities.tolist(),
        "final_training_probabilities": final_training_probabilities.tolist(),
        "final_full_dataset_probabilities": final_full_probabilities.tolist(),
        "initial_objective_mae": result.records[0].objective_mae,
        "final_objective_mae": result.records[-1].objective_mae,
        "best_objective_mae": min(objective_values),
        "best_iteration": int(np.argmin(objective_values)),
        "elapsed_seconds": result.elapsed_seconds,
        "objective_evaluations": result.objective_evaluations,
        "circuit_executions": result.circuit_executions,
        "total_shots": result.circuit_executions * SHOTS,
        "reproducibility_note": (
            "Aer uses fixed per-sample seeds for common random numbers; elapsed "
            "wall time varies by machine."
        ),
    }
    (OUTPUT / "task4_quantum_optimization.json").write_text(
        json.dumps(evidence, indent=2),
        encoding="utf-8",
    )

    print(
        f"initial MAE={evidence['initial_objective_mae']:.4f}; "
        f"final MAE={evidence['final_objective_mae']:.4f}; "
        f"best MAE={evidence['best_objective_mae']:.4f}"
    )
    print(
        f"{result.objective_evaluations} objective evaluations, "
        f"{result.circuit_executions} circuit executions, "
        f"{result.elapsed_seconds:.3f} seconds"
    )


if __name__ == "__main__":
    main()
