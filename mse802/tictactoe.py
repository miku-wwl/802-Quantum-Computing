"""Testable quantum Tic-Tac-Toe model for Assessment 2 Task 3."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import pi
from typing import Literal

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator


MoveName = Literal["Not", "O", "X", "SWAP"]
WINNING_LINES: tuple[tuple[int, int, int], ...] = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)


@dataclass(frozen=True)
class Move:
    """One gate-producing game action."""

    operation: MoveName
    cell: int
    other_cell: int | None = None


@dataclass(frozen=True)
class MeasurementResult:
    """Resolved one-shot board and its winning-line counts."""

    qiskit_bitstring: str
    board: tuple[str, ...]
    wins_x: int
    wins_o: int
    seed: int | None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class Board:
    """Nine independent qubits that are modified by game moves."""

    size = 9

    def __init__(self) -> None:
        self.circuit = QuantumCircuit(self.size, self.size, name="quantum_tic_tac_toe")
        self.labels = [str(index) for index in range(self.size)]
        self.history: list[Move] = []
        self.wins_x = 0
        self.wins_o = 0
        self.last_result: MeasurementResult | None = None
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

    @staticmethod
    def symbols_from_bitstring(bitstring: str) -> tuple[str, ...]:
        """Convert Qiskit's c8...c0 string to board cells 0...8."""

        compact = bitstring.replace(" ", "")
        if len(compact) != Board.size or set(compact) - {"0", "1"}:
            raise ValueError("bitstring must contain exactly nine binary digits")
        return tuple("O" if bit == "0" else "X" for bit in reversed(compact))

    @staticmethod
    def count_winners(board: tuple[str, ...] | list[str], player: str) -> int:
        """Count all of a player's completed rows, columns, and diagonals."""

        if len(board) != Board.size:
            raise ValueError("board must contain nine cells")
        if player not in {"O", "X"}:
            raise ValueError("player must be 'O' or 'X'")
        return sum(
            all(board[cell] == player for cell in winning_line)
            for winning_line in WINNING_LINES
        )

    def measurement_circuit(self) -> QuantumCircuit:
        """Return an independently measurable copy of the game circuit."""

        measured = self.circuit.copy(name="quantum_tic_tac_toe_measurement")
        measured.barrier(label="resolve board")
        measured.measure(range(self.size), range(self.size))
        return measured

    def measure(self, *, seed: int | None = None) -> MeasurementResult:
        """Resolve one game on Aer without mutating the stored move circuit."""

        simulator = AerSimulator()
        job = simulator.run(
            self.measurement_circuit(),
            shots=1,
            memory=True,
            seed_simulator=seed,
        )
        bitstring = job.result().get_memory()[0].replace(" ", "")
        symbols = self.symbols_from_bitstring(bitstring)
        self.labels = list(symbols)
        self.wins_x = self.count_winners(symbols, "X")
        self.wins_o = self.count_winners(symbols, "O")
        self.last_result = MeasurementResult(
            qiskit_bitstring=bitstring,
            board=symbols,
            wins_x=self.wins_x,
            wins_o=self.wins_o,
            seed=seed,
        )
        return self.last_result

    def reset(self) -> None:
        """Start a fresh round with no gates or state from the old game."""

        self.circuit = QuantumCircuit(self.size, self.size, name="quantum_tic_tac_toe")
        self.labels = [str(index) for index in range(self.size)]
        self.history.clear()
        self.wins_x = 0
        self.wins_o = 0
        self.last_result = None
        self._prepare_open_board()
