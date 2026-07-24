"""Portable ipywidgets interface for the Task 3 game."""

from __future__ import annotations

import ipywidgets as widgets
from IPython.display import display

from mse802.tictactoe import Board, MeasurementResult, MoveName


class TicTacToeWidget:
    """A local-Jupyter interface backed by :class:`mse802.tictactoe.Board`."""

    def __init__(self, board: Board | None = None) -> None:
        self.board = board or Board()
        self.pending_swap_cell: int | None = None
        self.operation = widgets.ToggleButtons(
            options=("Not", "O", "X", "SWAP"),
            value="O",
            description="Move:",
            button_style="",
        )
        self.cells = [
            widgets.Button(
                description=str(index),
                layout=widgets.Layout(width="92px", height="64px"),
                tooltip=f"Board cell {index}",
            )
            for index in range(self.board.size)
        ]
        for index, button in enumerate(self.cells):
            button.on_click(self._cell_callback(index))

        self.measure_button = widgets.Button(
            description="Measure",
            button_style="success",
            icon="check",
        )
        self.replay_button = widgets.Button(
            description="Replay",
            button_style="info",
            icon="refresh",
        )
        self.measure_button.on_click(self._on_measure)
        self.replay_button.on_click(self._on_replay)
        self.status = widgets.HTML(
            "<b>Ready.</b> Choose a move and a board cell. "
            "SWAP requires two different cells."
        )
        self.score = widgets.HTML("<b>Score:</b> unresolved")
        self.circuit_output = widgets.Output()
        self.grid = widgets.GridBox(
            self.cells,
            layout=widgets.Layout(
                grid_template_columns="repeat(3, 92px)",
                grid_gap="6px",
            ),
        )
        self.widget = widgets.VBox(
            [
                self.operation,
                self.grid,
                widgets.HBox([self.measure_button, self.replay_button]),
                self.status,
                self.score,
                self.circuit_output,
            ]
        )
        self._show_circuit()

    def _cell_callback(self, index: int):
        def callback(_: widgets.Button) -> None:
            self.play_cell(index)

        return callback

    def play_cell(self, cell: int) -> None:
        """Apply the selected operation, including SWAP's two-click flow."""

        operation: MoveName = self.operation.value
        if operation == "SWAP" and self.pending_swap_cell is None:
            self.pending_swap_cell = cell
            self.cells[cell].button_style = "warning"
            self.status.value = (
                f"<b>SWAP:</b> cell {cell} selected; choose a different cell."
            )
            return

        if operation == "SWAP":
            first_cell = self.pending_swap_cell
            self.pending_swap_cell = None
            if first_cell is not None:
                self.cells[first_cell].button_style = ""
            if first_cell == cell:
                self.status.value = "<b>SWAP cancelled:</b> choose two different cells."
                return
            self.board.apply_move("SWAP", first_cell, cell)
            self.status.value = f"Applied <b>SWAP</b> to cells {first_cell} and {cell}."
        else:
            self._clear_pending_swap()
            self.board.apply_move(operation, cell)
            self.status.value = f"Applied <b>{operation}</b> to cell {cell}."

        self._update_move_labels()
        self._show_circuit()

    def measure(self, *, seed: int | None = None) -> MeasurementResult:
        """Resolve the board, update the interface, and return the result."""

        self._clear_pending_swap()
        result = self.board.measure(seed=seed)
        for index, symbol in enumerate(result.board):
            self.cells[index].description = symbol
            self.cells[index].button_style = "danger" if symbol == "X" else "primary"
        self.score.value = (
            f"<b>Winning lines:</b> X = {result.wins_x}; O = {result.wins_o}"
        )
        self.status.value = (
            f"<b>Measured.</b> Qiskit bit order c8…c0: "
            f"<code>{result.qiskit_bitstring}</code>"
        )
        return result

    def replay(self) -> None:
        """Reset the model and every visual control for a new game."""

        self.board.reset()
        self._clear_pending_swap()
        self.operation.value = "O"
        for index, button in enumerate(self.cells):
            button.description = str(index)
            button.button_style = ""
        self.score.value = "<b>Score:</b> unresolved"
        self.status.value = "<b>New game.</b> All squares are in |+⟩."
        self._show_circuit()

    def _on_measure(self, _: widgets.Button) -> None:
        self.measure()

    def _on_replay(self, _: widgets.Button) -> None:
        self.replay()

    def _clear_pending_swap(self) -> None:
        if self.pending_swap_cell is not None:
            self.cells[self.pending_swap_cell].button_style = ""
        self.pending_swap_cell = None

    def _update_move_labels(self) -> None:
        for index, label in enumerate(self.board.labels):
            self.cells[index].description = label

    def _show_circuit(self) -> None:
        with self.circuit_output:
            self.circuit_output.clear_output(wait=True)
            display(self.board.circuit.draw("mpl", fold=30))
