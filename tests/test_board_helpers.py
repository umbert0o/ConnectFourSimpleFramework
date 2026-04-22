"""Tests for connect_four.board_helpers — AI utility functions."""

from __future__ import annotations

import pytest

from connect_four.board import Board
from connect_four.board_helpers import (
    count_pieces,
    evaluate_window,
    get_all_windows,
    get_column_heights,
)
from connect_four.player import EMPTY, Player


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def empty_board() -> Board:
    return Board()


@pytest.fixture
def board_with_horizontal_win() -> Board:
    b = Board()
    for c in range(4):
        b = b.drop_piece(c, Player.PLAYER_1)
    return b


@pytest.fixture
def board_with_vertical_win() -> Board:
    b = Board()
    for _ in range(4):
        b = b.drop_piece(3, Player.PLAYER_1)
    return b


# ---------------------------------------------------------------------------
# get_all_windows
# ---------------------------------------------------------------------------


class TestGetAllWindows:
    def test_empty_board_yields_correct_window_count(self, empty_board: Board) -> None:
        windows = list(get_all_windows(empty_board, size=4))
        assert len(windows) == 69

    def test_every_window_on_empty_board_is_all_zeros(self, empty_board: Board) -> None:
        for window in get_all_windows(empty_board, size=4):
            assert window == [EMPTY, EMPTY, EMPTY, EMPTY]

    def test_custom_size_3_window_count(self, empty_board: Board) -> None:
        windows = list(get_all_windows(empty_board, size=3))
        assert len(windows) == 98

    def test_non_standard_board_dimensions(self) -> None:
        b = Board(rows=5, cols=6)
        windows = list(get_all_windows(b, size=4))
        assert len(windows) == 39

    def test_yields_lists(self, empty_board: Board) -> None:
        for window in get_all_windows(empty_board, size=4):
            assert isinstance(window, list)

    def test_window_length_matches_size(self, empty_board: Board) -> None:
        for size in (2, 3, 4, 5):
            for window in get_all_windows(empty_board, size=size):
                assert len(window) == size

    def test_horizontal_win_window_captured(
        self, board_with_horizontal_win: Board
    ) -> None:
        windows = list(get_all_windows(board_with_horizontal_win, size=4))
        assert [1, 1, 1, 1] in windows

    def test_vertical_win_window_captured(self, board_with_vertical_win: Board) -> None:
        windows = list(get_all_windows(board_with_vertical_win, size=4))
        assert [1, 1, 1, 1] in windows

    def test_returns_generator(self, empty_board: Board) -> None:
        result = get_all_windows(empty_board)
        import types

        assert isinstance(result, types.GeneratorType)

    def test_size_larger_than_dimensions_yields_nothing(self) -> None:
        b = Board(rows=3, cols=3)
        windows = list(get_all_windows(b, size=4))
        assert len(windows) == 0


# ---------------------------------------------------------------------------
# count_pieces
# ---------------------------------------------------------------------------


class TestCountPieces:
    def test_all_player_1(self) -> None:
        assert count_pieces([1, 1, 1, 1], 1) == 4

    def test_none_of_player(self) -> None:
        assert count_pieces([2, 2, 0, 0], 1) == 0

    def test_mixed_window(self) -> None:
        assert count_pieces([1, 0, 2, 1], 1) == 2

    def test_count_empty(self) -> None:
        assert count_pieces([0, 0, 1, 2], EMPTY) == 2

    def test_empty_window(self) -> None:
        assert count_pieces([], 1) == 0

    def test_player_2(self) -> None:
        assert count_pieces([2, 2, 0, 1], 2) == 2


# ---------------------------------------------------------------------------
# get_column_heights
# ---------------------------------------------------------------------------


class TestGetColumnHeights:
    def test_empty_board(self, empty_board: Board) -> None:
        assert get_column_heights(empty_board) == [0, 0, 0, 0, 0, 0, 0]

    def test_single_piece(self, empty_board: Board) -> None:
        b = empty_board.drop_piece(3, Player.PLAYER_1)
        heights = get_column_heights(b)
        assert heights[3] == 1
        assert sum(heights) == 1

    def test_stacked_pieces(self, empty_board: Board) -> None:
        b = empty_board
        for _ in range(3):
            b = b.drop_piece(0, Player.PLAYER_1)
        heights = get_column_heights(b)
        assert heights[0] == 3
        assert heights[1] == 0

    def test_multiple_columns(self, empty_board: Board) -> None:
        b = empty_board
        b = b.drop_piece(0, Player.PLAYER_1)
        b = b.drop_piece(0, Player.PLAYER_2)
        b = b.drop_piece(3, Player.PLAYER_1)
        b = b.drop_piece(6, Player.PLAYER_2)
        heights = get_column_heights(b)
        assert heights == [2, 0, 0, 1, 0, 0, 1]

    def test_full_column(self, empty_board: Board) -> None:
        b = empty_board
        for _ in range(6):
            b = b.drop_piece(2, Player.PLAYER_1)
        assert get_column_heights(b)[2] == 6

    def test_non_standard_board(self) -> None:
        b = Board(rows=3, cols=4)
        b = b.drop_piece(1, Player.PLAYER_1)
        b = b.drop_piece(1, Player.PLAYER_2)
        b = b.drop_piece(3, Player.PLAYER_1)
        heights = get_column_heights(b)
        assert heights == [0, 2, 0, 1]
        assert len(heights) == 4

    def test_length_equals_cols(self, empty_board: Board) -> None:
        heights = get_column_heights(empty_board)
        assert len(heights) == empty_board.cols


# ---------------------------------------------------------------------------
# evaluate_window
# ---------------------------------------------------------------------------


class TestEvaluateWindow:
    def test_four_of_player_is_win(self) -> None:
        assert evaluate_window([1, 1, 1, 1], 1) == 100.0

    def test_four_of_player_2(self) -> None:
        assert evaluate_window([2, 2, 2, 2], 2) == 100.0

    def test_three_plus_empty(self) -> None:
        assert evaluate_window([1, 1, 1, 0], 1) == 10.0

    def test_three_plus_empty_order_independent(self) -> None:
        assert evaluate_window([0, 1, 1, 1], 1) == 10.0
        assert evaluate_window([1, 0, 1, 1], 1) == 10.0
        assert evaluate_window([1, 1, 0, 1], 1) == 10.0

    def test_two_plus_two_empty(self) -> None:
        assert evaluate_window([1, 1, 0, 0], 1) == 3.0

    def test_two_plus_two_empty_order_independent(self) -> None:
        assert evaluate_window([0, 1, 0, 1], 1) == 3.0

    def test_opponent_three_plus_empty(self) -> None:
        assert evaluate_window([2, 2, 2, 0], 1) == -10.0

    def test_opponent_three_player_absent(self) -> None:
        assert evaluate_window([2, 0, 2, 2], 1) == -10.0

    def test_opponent_three_from_player_2_perspective(self) -> None:
        assert evaluate_window([1, 1, 1, 0], 2) == -10.0

    def test_mixed_window_zero(self) -> None:
        assert evaluate_window([1, 2, 0, 0], 1) == 0.0

    def test_all_empty_zero(self) -> None:
        assert evaluate_window([0, 0, 0, 0], 1) == 0.0

    def test_one_piece_zero(self) -> None:
        assert evaluate_window([1, 0, 0, 0], 1) == 0.0

    def test_two_plus_opponent_one_zero(self) -> None:
        assert evaluate_window([1, 1, 2, 0], 1) == 0.0

    def test_win_greater_than_threat(self) -> None:
        assert evaluate_window([1, 1, 1, 1], 1) > evaluate_window([1, 1, 1, 0], 1)

    def test_threat_greater_than_build(self) -> None:
        assert evaluate_window([1, 1, 1, 0], 1) > evaluate_window([1, 1, 0, 0], 1)

    def test_build_greater_than_empty(self) -> None:
        assert evaluate_window([1, 1, 0, 0], 1) > evaluate_window([0, 0, 0, 0], 1)

    def test_build_greater_than_block(self) -> None:
        assert evaluate_window([1, 1, 0, 0], 1) > evaluate_window([2, 2, 2, 0], 1)

    def test_returns_float(self) -> None:
        result = evaluate_window([1, 1, 1, 1], 1)
        assert isinstance(result, float)
