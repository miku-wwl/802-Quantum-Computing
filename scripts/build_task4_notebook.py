"""Build the local Task 4 notebook from reviewable source cells."""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "submission" / "Task_4_Quantum_ML" / "Task_4_Quantum_ML.ipynb"


def build_notebook() -> None:
    notebook = nbf.v4.new_notebook()
    notebook["metadata"]["kernelspec"] = {
        "display_name": "Python 3 (MSE802)",
        "language": "python",
        "name": "python3",
    }
    notebook["metadata"]["language_info"] = {"name": "python", "version": "3.11"}
    notebook["cells"] = [
        nbf.v4.new_markdown_cell(
            """# MSE802 Assessment 2 — Task 4: Quantum Machine Learning

**Student:** ____________________  
**Runtime:** local Python 3.11 / Qiskit Aer, with optional Quokka validation

This notebook adapts the course-supplied `Quantum_ML_AS2.ipynb` to a local,
reproducible workflow. It analyses the image-classification circuit and its
input, records optimization metric and timing, and compares the quantum model
with a completely classical baseline."""
        ),
        nbf.v4.new_markdown_cell(
            """## 1. Environment and reproducibility

The supplied notebook imported `google.colab.files`, used a global NumPy random
state, and hard-coded an unencrypted Quokka URL. This version uses the locked
project environment, explicit seeds, project modules, and environment-based
backend configuration."""
        ),
        nbf.v4.new_code_cell(
            """from pathlib import Path
import sys

ROOT = Path.cwd()
if ROOT.name == "Task_4_Quantum_ML":
    ROOT = ROOT.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import qiskit

from mse802.quantum_ml import deterministic_split, generate_bar_stripe_data

SEED = 802
print(f"Qiskit version: {qiskit.__version__}")
print(f"Project root: {ROOT}")
print(f"Reproducibility seed: {SEED}")"""
        ),
        nbf.v4.new_markdown_cell(
            """## 2. Binary image dataset

The starter creates all two-bit binary words, repeats values to form vertical
stripe patterns and horizontal bar patterns, then removes all-black and
all-white images. With side length 2 this leaves exactly four 2×2 images: two
vertical stripes (label 0) and two horizontal bars (label 1). Each flattened
pixel becomes one qubit input, so the model uses four qubits."""
        ),
        nbf.v4.new_code_cell(
            """image_data = generate_bar_stripe_data(side_length=2)
dataset = image_data.features
labels = image_data.labels

figure, axes = plt.subplots(1, len(dataset), figsize=(8, 2.2))
for axis, pixels, label, name in zip(
    axes, dataset, labels, image_data.names, strict=True
):
    axis.imshow(pixels.reshape(2, 2), cmap="gray", vmin=0, vmax=1)
    axis.set_title(f"{name}\\nlabel={label}")
    axis.set_xticks([])
    axis.set_yticks([])
figure.suptitle("Task 4 bar/stripe dataset")
plt.tight_layout()
plt.show()

pd.DataFrame(dataset, index=image_data.names, columns=["p0", "p1", "p2", "p3"])"""
        ),
        nbf.v4.new_markdown_cell(
            """## 3. Deterministic starter split

The original 75/25 split was different on every run. A local
`numpy.random.Generator` seeded with 802 preserves the same split rule while
making the selected indices auditable. Because four samples yield only one
test sample, later effectiveness claims also report full-dataset and
leave-one-out measures; the single test item is not treated as a reliable
generalisation estimate."""
        ),
        nbf.v4.new_code_cell(
            """split = deterministic_split(dataset, labels, seed=SEED)
training, training_labels = split.training, split.training_labels
test, test_labels = split.test, split.test_labels

print("Training indices:", split.training_indices.tolist())
print("Training labels:", training_labels.tolist())
print("Test indices:", split.test_indices.tolist())
print("Test labels:", test_labels.tolist())

assert split.training_indices.tolist() == [3, 0, 2]
assert split.test_indices.tolist() == [1]
assert set(training_labels) == {0, 1}
print("Deterministic split checks: PASS")"""
        ),
        nbf.v4.new_markdown_cell(
            """## 4. Circuit and input analysis

### 4.1 Problem formulation and exact data-input location

The problem is binary image classification: vertical stripe patterns have
target 0 and horizontal bar patterns target 1. A sample is the flattened vector
$x=(x_0,x_1,x_2,x_3)$ in row-major pixel order. The **data enters only in the
basis-encoding loop**:

```python
for qubit, pixel in enumerate(sample):
    if pixel > 0.5:
        circuit.x(qubit)
```

Thus pixel $x_i=1$ prepares qubit $q_i$ in $|1\\rangle$; a zero leaves it in
$|0\\rangle$. The six angles are trainable model parameters, not data inputs.
Qiskit's displayed bit order does not change this index mapping."""
        ),
        nbf.v4.new_code_cell(
            """from mse802.quantum_ml import (
    create_quantum_classifier_circuit,
    exact_output_probability,
    generate_pairs,
    parameter_count,
)

N_QUBITS = dataset.shape[1]
N_PARAMETERS = parameter_count(N_QUBITS)
PAIR_SCHEDULE = generate_pairs(N_QUBITS)

print("Qubit/pixel mapping:", {f"p{i}": f"q{i}" for i in range(N_QUBITS)})
print("Recursive pairs:", PAIR_SCHEDULE)
print("Trainable parameters:", N_PARAMETERS)
print("Readout: q3 -> c0")"""
        ),
        nbf.v4.new_markdown_cell(
            """### 4.2 Recursive RY–RY–CX model

Each pair $(i,j)$ receives $R_Y(\\theta_k)$ on $q_i$,
$R_Y(\\theta_{k+1})$ on $q_j$, then CNOT with $q_i$ as control and $q_j$ as
target. For four qubits the post-order recursion produces:

1. $(q_0,q_1)$ — combine the first two pixels;
2. $(q_2,q_3)$ — combine the last two pixels; and
3. $(q_1,q_3)$ — combine the two branches into output qubit $q_3$.

There are $n-1=3$ blocks and therefore $2(n-1)=6$ angles. RY can create
superposition from basis inputs; subsequent CNOTs can then create
entanglement. Only $q_3$ is measured into the one-bit classical register, so
the model prediction is $P(c_0=1)$."""
        ),
        nbf.v4.new_code_cell(
            """zero_angles = np.zeros(N_PARAMETERS)
example_circuit = create_quantum_classifier_circuit(dataset[0], zero_angles)
display(example_circuit.draw("mpl", fold=30))
print(example_circuit)

zero_predictions = np.array(
    [exact_output_probability(sample, zero_angles) for sample in dataset]
)
print("Exact P(output=1) at zero angles:", zero_predictions)
assert np.allclose(zero_predictions, 0.0, atol=1e-12)"""
        ),
        nbf.v4.new_markdown_cell(
            """### 4.3 Zero-angle diagnostic

With every RY angle zero, the three CNOTs form a parity tree and $q_3$ holds
$x_0\\oplus x_1\\oplus x_2\\oplus x_3$. Every supplied image contains exactly
two white pixels, so all four outputs are 0. This correctly proves that the
untrained model cannot distinguish the classes; non-zero learned rotations are
essential. The exact statevector calculation avoids confusing shot noise with
model behaviour."""
        ),
        nbf.v4.new_markdown_cell(
            """## 5. Switchable quantum backend

One circuit constructor feeds three execution modes:

- **exact** — statevector $P(c_0=1)$, with no shots;
- **aer** — local shot-based execution with an explicit simulator seed; and
- **quokka** — the same OpenQASM subset submitted to the configured endpoint.

Optimization uses Aer locally. A fixed six-angle vector is evaluated separately
on the exact statevector, Aer, and real Quokka so backend validation does not
multiply the number of remote optimizer calls. The captured response is saved
with endpoint, timestamp, QASM, counts, and raw payload."""
        ),
        nbf.v4.new_code_cell(
            """import json

from mse802.quantum_ml import execute_quantum_classifier

FIXED_VALIDATION_ANGLES = np.array([0.2, -0.4, 0.6, 0.8, -0.3, 0.5])
backend_evidence = json.loads(
    (ROOT / "submission" / "Task_4_Quantum_ML" /
     "task4_backend_validation.json").read_text()
)

backend_rows = []
for index, (sample, name) in enumerate(zip(dataset, image_data.names, strict=True)):
    exact = execute_quantum_classifier(
        sample, FIXED_VALIDATION_ANGLES, backend="exact"
    )
    aer = execute_quantum_classifier(
        sample,
        FIXED_VALIDATION_ANGLES,
        backend="aer",
        shots=256,
        seed=SEED + index,
    )
    remote = backend_evidence["records"][index]["quokka"]
    backend_rows.append(
        {
            "sample": name,
            "exact P(1)": exact.probability_one,
            "Aer P(1)": aer.probability_one,
            "Quokka P(1)": remote["probability_one"],
            "|Aer-Quokka|": abs(
                aer.probability_one - remote["probability_one"]
            ),
        }
    )

pd.DataFrame(backend_rows)"""
        ),
        nbf.v4.new_markdown_cell(
            """The fixed-vector comparison is a backend check, not evidence of training
quality. Exact and Aer results should differ only by finite-shot sampling.
Any larger systematic Quokka difference is reported rather than silently
replacing the remote result; optimization and the classical benchmark remain
locally reproducible.

In the captured run, the largest absolute Aer–Quokka probability difference
across the four samples is **0.015625** (four counts out of 256). This is small
relative to the sampling uncertainty and provides no evidence of a systematic
backend disagreement for this circuit."""
        ),
        nbf.v4.new_markdown_cell(
            """## 6. Optimization trace

Per-iteration objective values and elapsed times are added with two required
plots."""
        ),
        nbf.v4.new_markdown_cell(
            """## 7. Classical no-circuit baseline

A model with no quantum circuit or quantum simulator is added for a fair
efficiency/effectiveness comparison."""
        ),
        nbf.v4.new_markdown_cell(
            """## 8. Results, limitations, and conclusion

Benchmark evidence and interpretation are added after both implementations
are complete."""
        ),
    ]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(notebook, OUTPUT)


if __name__ == "__main__":
    build_notebook()
