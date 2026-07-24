"""Build the local Task 3 notebook from reviewable source cells."""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "submission" / "Task_3_Quantum_Tic_Tac_Toe" / "Task_3_Quantum_Tic_Tac_Toe.ipynb"


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
            """# MSE802 Assessment 2 — Task 3: Quantum Tic-Tac-Toe

**Student:** ____________________  
**Runtime:** local Python 3.11 / Qiskit Aer

This notebook is a local-Jupyter adaptation of the course-supplied
`Quantum_Tic_Tac_Toe__AS2.ipynb`. The original Google Colab dependency is
removed; the completed game uses standard `ipywidgets` and testable project
code. See `SOURCE_NOTE.md` for the adaptation boundary."""
        ),
        nbf.v4.new_markdown_cell(
            """## 1. Environment and local imports

The assessment starter installed packages inside Colab and used
`google.colab.widgets.Grid`. This version relies on the locked project
environment and portable `ipywidgets` components."""
        ),
        nbf.v4.new_code_cell(
            """from pathlib import Path
import sys

ROOT = Path.cwd()
if ROOT.name == "Task_3_Quantum_Tic_Tac_Toe":
    ROOT = ROOT.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import ipywidgets as widgets
import matplotlib.pyplot as plt
import numpy as np
import qiskit
from IPython.display import display
from qiskit_aer import AerSimulator

print(f"Qiskit version: {qiskit.__version__}")
print(f"Project root: {ROOT}")"""
        ),
        nbf.v4.new_markdown_cell(
            """## 2. Starter-code gap map

The supplied notebook left four gate operations, the eight winning triples,
and a reliable two-cell SWAP selection flow incomplete. Its board rendering
also depended on a Colab-only grid widget. The following sections complete
those items while keeping the starter's central idea: each move appends a
quantum gate and a one-shot measurement resolves the board."""
        ),
        nbf.v4.new_markdown_cell(
            """## 3. Completed game model

Implementation is added in the next milestones and imported from
`mse802.tictactoe` so it can be tested independently of the notebook UI."""
        ),
        nbf.v4.new_markdown_cell(
            """## 4. Local interactive game

The native `ipywidgets` interface is added after the game model is complete."""
        ),
        nbf.v4.new_markdown_cell(
            """## 5. Reproducible game evidence

Multiple deterministic and sampled games, circuit evidence, and outcome
analysis are added after the automated checks pass."""
        ),
    ]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(notebook, OUTPUT)


if __name__ == "__main__":
    build_notebook()
