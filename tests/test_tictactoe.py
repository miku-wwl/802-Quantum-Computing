from __future__ import annotations

from mse802.tictactoe import Board, WINNING_LINES
from mse802.tictactoe_ui import TicTacToeWidget


def test_all_move_types_append_the_expected_gates() -> None:
    board = Board()
    board.apply_move("O", 0)
    board.apply_move("X", 1)
    board.apply_move("Not", 2)
    board.apply_move("SWAP", 0, 1)

    assert [instruction.operation.name for instruction in board.circuit.data[-4:]] == [
        "ry",
        "ry",
        "x",
        "swap",
    ]
    assert [move["operation"] for move in board.move_log()] == [
        "O",
        "X",
        "Not",
        "SWAP",
    ]


def test_o_x_and_not_have_deterministic_semantics() -> None:
    board = Board()
    board.apply_move("O", 0)
    board.apply_move("X", 1)
    board.apply_move("O", 2)
    board.apply_move("Not", 2)

    result = board.measure(seed=802)

    assert result.board[0] == "O"
    assert result.board[1] == "X"
    assert result.board[2] == "X"


def test_swap_exchanges_complete_cell_states() -> None:
    board = Board()
    board.apply_move("O", 0)
    board.apply_move("X", 1)
    board.apply_move("SWAP", 0, 1)

    result = board.measure(seed=802)

    assert result.board[0] == "X"
    assert result.board[1] == "O"


def test_winning_lines_are_complete_and_counted() -> None:
    assert len(WINNING_LINES) == 8
    assert len(set(WINNING_LINES)) == 8
    for line in WINNING_LINES:
        board = ["O"] * Board.size
        for cell in line:
            board[cell] = "X"
        assert Board.count_winners(board, "X") >= 1

    full_x_board = ["X"] * Board.size
    assert Board.count_winners(full_x_board, "X") == 8
    assert Board.count_winners(full_x_board, "O") == 0


def test_qiskit_bit_order_is_reversed_for_board_cells() -> None:
    symbols = Board.symbols_from_bitstring("100000001")
    assert symbols[0] == "X"
    assert symbols[8] == "X"
    assert symbols[1:8] == ("O",) * 7


def test_measurement_does_not_mutate_game_circuit_and_reset_is_clean() -> None:
    board = Board()
    board.apply_move("X", 4)
    instructions_before = len(board.circuit.data)
    board.measure(seed=802)

    assert len(board.circuit.data) == instructions_before
    assert not any(item.operation.name == "measure" for item in board.circuit.data)

    board.reset()
    assert board.history == []
    assert board.last_result is None
    assert board.labels == [str(index) for index in range(9)]
    assert not any(item.operation.name == "measure" for item in board.circuit.data)


def test_widget_swap_flow_and_replay(monkeypatch) -> None:
    monkeypatch.setattr(TicTacToeWidget, "_show_circuit", lambda self: None)
    game = TicTacToeWidget()
    game.operation.value = "SWAP"

    game.play_cell(2)
    assert game.pending_swap_cell == 2

    game.play_cell(6)
    assert game.pending_swap_cell is None
    assert game.board.move_log()[-1] == {
        "operation": "SWAP",
        "cell": 2,
        "other_cell": 6,
    }

    game.replay()
    assert game.board.move_log() == []
    assert [button.description for button in game.cells] == [str(i) for i in range(9)]
