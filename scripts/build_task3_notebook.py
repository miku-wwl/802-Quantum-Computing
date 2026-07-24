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

The model lives in `mse802.tictactoe` so it can be tested independently of the
interface. Each square begins in

$$|+\\rangle=\\frac{|0\\rangle+|1\\rangle}{\\sqrt{2}}.$$

The four moves append these gates:

- **O:** $R_Y(-\\pi/2)|+\\rangle=|0\\rangle$;
- **X:** $R_Y(+\\pi/2)|+\\rangle=|1\\rangle$;
- **Not:** Pauli-$X$, interchanging the $|0\\rangle$ and $|1\\rangle$
  amplitudes; and
- **SWAP:** exchanges the complete states of two selected qubits.

The labels O = measured 0 and X = measured 1 follow the supplied comments
“rotation toward $|0\\rangle$” and “rotation toward $|1\\rangle$”."""
        ),
        nbf.v4.new_code_cell(
            """from mse802.tictactoe import Board

gate_demo = Board()
gate_demo.apply_move("O", 0)
gate_demo.apply_move("X", 1)
gate_demo.apply_move("Not", 2)
gate_demo.apply_move("SWAP", 0, 1)

print("Recorded moves:")
for move in gate_demo.move_log():
    print(move)
display(gate_demo.circuit.draw("mpl", fold=30))"""
        ),
        nbf.v4.new_markdown_cell(
            """### Measurement, bit order, and winning lines

The eight winning triples are three rows, three columns, and two diagonals.
Aer returns a nine-character string in classical-bit order
$c_8c_7\\ldots c_0$, so it must be reversed before character 0 is assigned to
board cell 0. A measured 0 is O and a measured 1 is X.

Measurement is appended only to a copy of the move circuit. This preserves the
unmeasured circuit for inspection. `reset()` creates an entirely new circuit,
re-prepares all nine $|+\\rangle$ states, and clears scores and history."""
        ),
        nbf.v4.new_code_cell(
            """from mse802.tictactoe import WINNING_LINES

deterministic_row = Board()
for cell in range(9):
    deterministic_row.apply_move("O" if cell < 3 else "X", cell)

row_result = deterministic_row.measure(seed=802)
print("Winning triples:", WINNING_LINES)
print("Qiskit c8...c0:", row_result.qiskit_bitstring)
print("Board cells 0...8:", row_result.board)
print(f"X wins: {row_result.wins_x}; O wins: {row_result.wins_o}")"""
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
