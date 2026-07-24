"""Generate the dataset and circuit evidence used in Task 4 analysis."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import qiskit
from qiskit import qasm2


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "submission" / "Task_4_Quantum_ML"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mse802.quantum_ml import (
    create_quantum_classifier_circuit,
    exact_output_probability,
    generate_bar_stripe_data,
    generate_pairs,
    parameter_count,
)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    data = generate_bar_stripe_data(side_length=2)
    angles = np.zeros(parameter_count(data.features.shape[1]))

    dataset_figure, axes = plt.subplots(1, len(data.features), figsize=(8, 2.2))
    for axis, pixels, label, name in zip(
        axes,
        data.features,
        data.labels,
        data.names,
        strict=True,
    ):
        axis.imshow(pixels.reshape(2, 2), cmap="gray", vmin=0, vmax=1)
        axis.set_title(f"{name}\nlabel={label}")
        axis.set_xticks([])
        axis.set_yticks([])
    dataset_figure.suptitle("Task 4 input dataset")
    dataset_figure.tight_layout()
    dataset_figure.savefig(
        OUTPUT / "task4_dataset.png",
        dpi=180,
        bbox_inches="tight",
    )
    plt.close(dataset_figure)

    example = create_quantum_classifier_circuit(data.features[0], angles)
    (OUTPUT / "task4_example_circuit.qasm").write_text(
        qasm2.dumps(example),
        encoding="utf-8",
    )
    circuit_figure = example.draw("mpl", fold=30)
    circuit_figure.savefig(
        OUTPUT / "task4_example_circuit.png",
        dpi=180,
        bbox_inches="tight",
    )
    plt.close(circuit_figure)

    evidence = {
        "qiskit_version": qiskit.__version__,
        "side_length": data.side_length,
        "features": data.features.tolist(),
        "labels": data.labels.tolist(),
        "names": list(data.names),
        "qubits": int(data.features.shape[1]),
        "classical_bits": 1,
        "output_qubit": int(data.features.shape[1] - 1),
        "pair_schedule": [list(pair) for pair in generate_pairs(4)],
        "parameter_count": parameter_count(4),
        "input_rule": "pixel i == 1 appends X on qubit i",
        "zero_angle_output_probabilities": [
            exact_output_probability(sample, angles) for sample in data.features
        ],
        "example_operation_counts": dict(example.count_ops()),
        "example_depth": example.depth(),
    }
    (OUTPUT / "task4_circuit_analysis.json").write_text(
        json.dumps(evidence, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    main()
