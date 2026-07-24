"""Testable quantum Tic-Tac-Toe model for Assessment 2 Task 3."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import pi
from typing import Literal

from qiskit import QuantumCircuit


MoveName = Literal["Not", "O", "X", "SWAP"]


@dataclass(frozen=True)
class Move:
    """One gate-producing game action."""

    operation: MoveName
    cell: int
    other_cell: int | None = None


class Board:
    """Nine independent qubits that are modified by game moves."""

    size = 9

    def __init__(self) -> None:
        self.circuit = QuantumCircuit(self.size, self.size, name="quantum_tic_tac_toe")
        self.labels = [str(index) for index in range(self.size)]
        self.history: list[Move] = []
        self.wins_x = 0
        self.wins_o = 0
        self._prepare_open_board()

    def _prepare_open_board(self) -> None:
        """Prepare every square in |+>, an equal O/X superposition."""

        for qubit in range(self.size):
            self.circuit.reset(qubit)
            self.circuit.h(qubit)
        self.circuit.barrier(label="open board")

    @staticmethod
    def _validate_cell(cell: int) -> int:
        if isinstance(cell, bool) or not isinstance(cell, int):
            raise TypeError("cell must be an integer")
        if not 0 <= cell < Board.size:
            raise ValueError(f"cell must be between 0 and {Board.size - 1}")
        return cell

    def apply_move(
        self,
        operation: MoveName,
        cell: int,
        other_cell: int | None = None,
    ) -> Move:
        """Append the gate represented by a player action.

        Each qubit starts in |+>. Therefore RY(-pi/2)|+> = |0> for O and
        RY(+pi/2)|+> = |1> for X. Not applies Pauli-X. SWAP requires two
        distinct cells and exchanges their complete quantum states.
        """

        cell = self._validate_cell(cell)
        if operation == "Not":
            self.circuit.x(cell)
            self.labels[cell] += " · N"
        elif operation == "O":
            self.circuit.ry(-pi / 2, cell)
            self.labels[cell] += " · O"
        elif operation == "X":
            self.circuit.ry(pi / 2, cell)
            self.labels[cell] += " · X"
        elif operation == "SWAP":
            if other_cell is None:
                raise ValueError("SWAP requires other_cell")
            other_cell = self._validate_cell(other_cell)
            if cell == other_cell:
                raise ValueError("SWAP cells must be different")
            self.circuit.swap(cell, other_cell)
            self.labels[cell] += f" · S{other_cell}"
            self.labels[other_cell] += f" · S{cell}"
        else:
            raise ValueError(f"unknown operation: {operation!r}")

        move = Move(operation=operation, cell=cell, other_cell=other_cell)
        self.history.append(move)
        return move

    def move_log(self) -> list[dict[str, str | int | None]]:
        """Return a JSON-serialisable move history."""

        return [asdict(move) for move in self.history]
