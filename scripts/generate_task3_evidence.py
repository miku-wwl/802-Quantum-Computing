"""Run four reproducible games and save Task 3 assessment evidence."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import qiskit
from qiskit import qasm2

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "submission" / "Task_3_Quantum_Tic_Tac_Toe"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mse802.tictactoe import Board


def deterministic_rows() -> Board:
    board = Board()
    for cell in range(9):
        board.apply_move("O" if cell < 3 else "X", cell)
    return board


def not_diagonal() -> Board:
    board = Board()
    for cell in range(9):
        board.apply_move("O", cell)
    for cell in (0, 4, 8):
        board.apply_move("Not", cell)
    return board


def swap_and_not() -> Board:
    board = Board()
    board.apply_move("O", 0)
    board.apply_move("X", 1)
    board.apply_move("SWAP", 0, 1)
    board.apply_move("Not", 1)
    board.apply_move("X", 2)
    for cell in range(3, 9):
        board.apply_move("O", cell)
    return board


def untouched_superposition() -> Board:
    return Board()


def save_circuit(board: Board, stem: str) -> None:
    measured = board.measurement_circuit()
    (OUTPUT / f"{stem}.qasm").write_text(qasm2.dumps(measured), encoding="utf-8")
    figure = measured.draw("mpl", fold=30)
    figure.savefig(OUTPUT / f"{stem}.png", dpi=160, bbox_inches="tight")
    plt.close(figure)


def save_board_summary(records: list[dict[str, object]]) -> None:
    figure, axes = plt.subplots(2, 2, figsize=(9.2, 8.2), constrained_layout=True)
    colours = {"X": "#ef8354", "O": "#4f86c6"}
    for axis, record in zip(axes.flat, records, strict=True):
        board = record["result"]["board"]
        axis.set_xlim(0, 3)
        axis.set_ylim(0, 3)
        axis.set_aspect("equal")
        axis.set_xticks([])
        axis.set_yticks([])
        for cell, symbol in enumerate(board):
            row, column = divmod(cell, 3)
            y = 2 - row
            rectangle = plt.Rectangle(
                (column, y),
                1,
                1,
                facecolor=colours[symbol],
                edgecolor="white",
                linewidth=3,
            )
            axis.add_patch(rectangle)
            axis.text(
                column + 0.5,
                y + 0.5,
                symbol,
                ha="center",
                va="center",
                color="white",
                fontsize=24,
                fontweight="bold",
            )
        result = record["result"]
        axis.set_title(
            f"{record['title']}\nX wins={result['wins_x']}, O wins={result['wins_o']}",
            fontsize=9.5,
        )
    figure.suptitle("Quantum Tic-Tac-Toe: four resolved games", fontsize=14)
    figure.savefig(OUTPUT / "task3_four_game_summary.png", dpi=180, bbox_inches="tight")
    plt.close(figure)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    scenarios = (
        ("game_1_rows", "Game 1 — direct O/X rotations", deterministic_rows(), 802),
        ("game_2_not", "Game 2 — Not creates X diagonal", not_diagonal(), 803),
        ("game_3_swap", "Game 3 — SWAP and Not", swap_and_not(), 804),
        ("game_4_open", "Game 4 — unresolved |+⟩ board", untouched_superposition(), 805),
    )
    records: list[dict[str, object]] = []
    for stem, title, board, seed in scenarios:
        result = board.measure(seed=seed)
        save_circuit(board, stem)
        records.append(
            {
                "id": stem,
                "title": title,
                "seed": seed,
                "moves": board.move_log(),
                "result": result.to_dict(),
                "circuit": {
                    "qubits": board.circuit.num_qubits,
                    "classical_bits": board.circuit.num_clbits,
                    "depth_before_measurement": board.circuit.depth(),
                    "operation_counts": dict(board.circuit.count_ops()),
                },
            }
        )

    evidence = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "qiskit_version": qiskit.__version__,
        "backend": "qiskit_aer.AerSimulator",
        "shots_per_game": 1,
        "bit_mapping": "Qiskit c8...c0 is reversed to board cells 0...8",
        "games": records,
    }
    (OUTPUT / "task3_game_evidence.json").write_text(
        json.dumps(evidence, indent=2),
        encoding="utf-8",
    )
    save_board_summary(records)
    for record in records:
        result = record["result"]
        print(
            record["id"],
            "".join(result["board"]),
            f"X={result['wins_x']}",
            f"O={result['wins_o']}",
        )


if __name__ == "__main__":
    main()
