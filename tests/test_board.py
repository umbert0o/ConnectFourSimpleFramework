"""Comprehensive pytest tests for the Board class."""

import pytest

from connect_four.board import Board
from connect_four.player import EMPTY, Player


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def empty_board() -> Board:
    """Standard 6x7 empty board."""
    return Board()


@pytest.fixture
def board_with_row_of_4() -> Board:
    """Board with PLAYER_1 having a horizontal win on the bottom row."""
    b = Board()
    b = b.drop_piece(0, Player.PLAYER_1)
    b = b.drop_piece(1, Player.PLAYER_1)
    b = b.drop_piece(2, Player.PLAYER_1)
    b = b.drop_piece(3, Player.PLAYER_1)
    return b


# ---------------------------------------------------------------------------
# 1. Creation
# ---------------------------------------------------------------------------


class TestBoardCreation:
    def test_default_dimensions(self, empty_board: Board) -> None:
        assert empty_board.rows == 6
        assert empty_board.cols == 7

    def test_all_cells_empty(self, empty_board: Board) -> None:
        for r in range(empty_board.rows):
            for c in range(empty_board.cols):
                assert empty_board.get_cell(r, c) == EMPTY

    def test_custom_dimensions(self) -> None:
        b = Board(rows=5, cols=6)
        assert b.rows == 5
        assert b.cols == 6
        assert b.get_cell(4, 5) == EMPTY


# ---------------------------------------------------------------------------
# 2. drop_piece
# ---------------------------------------------------------------------------


class TestDropPiece:
    def test_piece_falls_to_bottom(self, empty_board: Board) -> None:
        b = empty_board.drop_piece(3, Player.PLAYER_1)
        assert b.get_cell(5, 3) == Player.PLAYER_1

    def test_pieces_stack_in_same_column(self, empty_board: Board) -> None:
        b = empty_board.drop_piece(2, Player.PLAYER_1)
        b = b.drop_piece(2, Player.PLAYER_2)
        assert b.get_cell(5, 2) == Player.PLAYER_1
        assert b.get_cell(4, 2) == Player.PLAYER_2

    def test_returns_new_board_immutability(self, empty_board: Board) -> None:
        _ = empty_board.drop_piece(0, Player.PLAYER_1)
        assert empty_board.get_cell(5, 0) == EMPTY

    def test_independent_branches(self, empty_board: Board) -> None:
        b1 = empty_board.drop_piece(0, Player.PLAYER_1)
        b2 = empty_board.drop_piece(1, Player.PLAYER_2)
        assert b1.get_cell(5, 0) == Player.PLAYER_1
        assert b1.get_cell(5, 1) == EMPTY
        assert b2.get_cell(5, 1) == Player.PLAYER_2
        assert b2.get_cell(5, 0) == EMPTY

    def test_invalid_column_negative_raises(self, empty_board: Board) -> None:
        with pytest.raises(ValueError, match="out of range"):
            empty_board.drop_piece(-1, Player.PLAYER_1)

    def test_invalid_column_too_large_raises(self, empty_board: Board) -> None:
        with pytest.raises(ValueError, match="out of range"):
            empty_board.drop_piece(7, Player.PLAYER_1)

    def test_full_column_raises(self, empty_board: Board) -> None:
        b = empty_board
        for _ in range(6):
            b = b.drop_piece(0, Player.PLAYER_1)
        with pytest.raises(ValueError, match="full"):
            b.drop_piece(0, Player.PLAYER_2)


# ---------------------------------------------------------------------------
# 3. is_valid_move
# ---------------------------------------------------------------------------


class TestIsValidMove:
    def test_valid_columns_on_empty_board(self, empty_board: Board) -> None:
        for c in range(7):
            assert empty_board.is_valid_move(c) is True

    def test_negative_column(self, empty_board: Board) -> None:
        assert empty_board.is_valid_move(-1) is False

    def test_column_out_of_range(self, empty_board: Board) -> None:
        assert empty_board.is_valid_move(7) is False
        assert empty_board.is_valid_move(100) is False

    def test_full_column_is_invalid(self, empty_board: Board) -> None:
        b = empty_board
        for _ in range(6):
            b = b.drop_piece(3, Player.PLAYER_1)
        assert b.is_valid_move(3) is False


# ---------------------------------------------------------------------------
# 4. get_valid_moves
# ---------------------------------------------------------------------------


class TestGetValidMoves:
    def test_empty_board(self, empty_board: Board) -> None:
        assert empty_board.get_valid_moves() == [0, 1, 2, 3, 4, 5, 6]

    def test_partial_board(self) -> None:
        b = Board()
        for _ in range(6):
            b = b.drop_piece(1, Player.PLAYER_1)
        for _ in range(6):
            b = b.drop_piece(5, Player.PLAYER_1)
        moves = b.get_valid_moves()
        assert 1 not in moves
        assert 5 not in moves
        assert 0 in moves
        assert 6 in moves


# ---------------------------------------------------------------------------
# 5. check_winner — all four directions + no-winner cases
# ---------------------------------------------------------------------------


class TestCheckWinner:
    def _build_horizontal_win(self) -> Board:
        b = Board()
        for c in range(4):
            b = b.drop_piece(c, Player.PLAYER_1)
        return b

    def _build_vertical_win(self) -> Board:
        b = Board()
        for _ in range(4):
            b = b.drop_piece(3, Player.PLAYER_1)
        return b

    def _build_diagonal_down_right(self) -> Board:
        """Build a diagonal win going down-right (dr=1, dc=1).

        Layout (bottom-up stacking in columns 0-3):
          col 0: P1                     row 5
          col 1: P2, P1                 rows 5, 4
          col 2: P2, P2, P1             rows 5, 4, 3
          col 3: P2, P2, P2, P1         rows 5, 4, 3, 2  ← P1 wins here
        """
        b = Board()
        b = b.drop_piece(0, Player.PLAYER_1)
        b = b.drop_piece(1, Player.PLAYER_2)
        b = b.drop_piece(1, Player.PLAYER_1)
        b = b.drop_piece(2, Player.PLAYER_2)
        b = b.drop_piece(2, Player.PLAYER_2)
        b = b.drop_piece(2, Player.PLAYER_1)
        b = b.drop_piece(3, Player.PLAYER_2)
        b = b.drop_piece(3, Player.PLAYER_2)
        b = b.drop_piece(3, Player.PLAYER_2)
        b = b.drop_piece(3, Player.PLAYER_1)
        return b

    def _build_diagonal_down_left(self) -> Board:
        """Build a diagonal win going down-left (dr=1, dc=-1).

        Layout (bottom-up stacking in columns 3-6):
          col 6: P1                     row 5
          col 5: P2, P1                 rows 5, 4
          col 4: P2, P2, P1             rows 5, 4, 3
          col 3: P2, P2, P2, P1         rows 5, 4, 3, 2  ← P1 wins here
        """
        b = Board()
        b = b.drop_piece(6, Player.PLAYER_1)
        b = b.drop_piece(5, Player.PLAYER_2)
        b = b.drop_piece(5, Player.PLAYER_1)
        b = b.drop_piece(4, Player.PLAYER_2)
        b = b.drop_piece(4, Player.PLAYER_2)
        b = b.drop_piece(4, Player.PLAYER_1)
        b = b.drop_piece(3, Player.PLAYER_2)
        b = b.drop_piece(3, Player.PLAYER_2)
        b = b.drop_piece(3, Player.PLAYER_2)
        b = b.drop_piece(3, Player.PLAYER_1)
        return b

    def test_horizontal_win(self) -> None:
        b = self._build_horizontal_win()
        assert b.check_winner() == Player.PLAYER_1

    def test_vertical_win(self) -> None:
        b = self._build_vertical_win()
        assert b.check_winner() == Player.PLAYER_1

    def test_diagonal_down_right(self) -> None:
        b = self._build_diagonal_down_right()
        assert b.check_winner() == Player.PLAYER_1

    def test_diagonal_down_left(self) -> None:
        b = self._build_diagonal_down_left()
        assert b.check_winner() == Player.PLAYER_1

    def test_no_winner_on_empty_board(self, empty_board: Board) -> None:
        assert empty_board.check_winner() is None

    def test_no_winner_partial_board(self) -> None:
        b = Board()
        b = b.drop_piece(0, Player.PLAYER_1)
        b = b.drop_piece(1, Player.PLAYER_2)
        b = b.drop_piece(2, Player.PLAYER_1)
        assert b.check_winner() is None

    def test_winner_returns_player_number(self) -> None:
        """check_winner returns int 1 or 2, matching Player values."""
        b1 = self._build_horizontal_win()
        result = b1.check_winner()
        assert result in (1, 2)
        assert result == Player.PLAYER_1

    def test_player_2_can_win(self) -> None:
        """PLAYER_2 wins horizontally."""
        b = Board()
        for c in range(4):
            b = b.drop_piece(c, Player.PLAYER_2)
        assert b.check_winner() == Player.PLAYER_2


# ---------------------------------------------------------------------------
# 6. is_full
# ---------------------------------------------------------------------------


class TestIsFull:
    def test_empty_board_not_full(self, empty_board: Board) -> None:
        assert empty_board.is_full() is False

    def test_partial_board_not_full(self) -> None:
        b = Board()
        b = b.drop_piece(0, Player.PLAYER_1)
        b = b.drop_piece(3, Player.PLAYER_2)
        assert b.is_full() is False

    def test_full_board(self) -> None:
        """Fill the entire board in a draw pattern (no winner)."""
        b = Board()
        for col in range(7):
            for row in range(6):
                player = Player.PLAYER_1 if (col + row) % 2 == 0 else Player.PLAYER_2
                b = b.drop_piece(col, player)
        assert b.is_full() is True
        assert b.get_valid_moves() == []


# ---------------------------------------------------------------------------
# 7. get_cell
# ---------------------------------------------------------------------------


class TestGetCell:
    def test_empty_cell(self, empty_board: Board) -> None:
        assert empty_board.get_cell(0, 0) == EMPTY
        assert empty_board.get_cell(5, 6) == EMPTY

    def test_after_moves(self) -> None:
        b = Board()
        b = b.drop_piece(0, Player.PLAYER_1)
        b = b.drop_piece(0, Player.PLAYER_2)
        assert b.get_cell(5, 0) == Player.PLAYER_1
        assert b.get_cell(4, 0) == Player.PLAYER_2
        assert b.get_cell(3, 0) == EMPTY


# ---------------------------------------------------------------------------
# 8. __str__
# ---------------------------------------------------------------------------


class TestStr:
    def test_returns_string(self, empty_board: Board) -> None:
        assert isinstance(str(empty_board), str)

    def test_contains_grid_and_separator(self, empty_board: Board) -> None:
        s = str(empty_board)
        assert "-" in s
        assert "0" in s

    def test_shows_piece_after_drop(self) -> None:
        b = Board()
        b = b.drop_piece(0, Player.PLAYER_1)
        s = str(b)
        assert "1" in s


# ---------------------------------------------------------------------------
# 9. rows / cols properties
# ---------------------------------------------------------------------------


class TestProperties:
    def test_rows(self, empty_board: Board) -> None:
        assert empty_board.rows == 6

    def test_cols(self, empty_board: Board) -> None:
        assert empty_board.cols == 7


# ---------------------------------------------------------------------------
# 10. Column boundary
# ---------------------------------------------------------------------------


class TestColumnBoundary:
    def test_col_zero_works(self, empty_board: Board) -> None:
        b = empty_board.drop_piece(0, Player.PLAYER_1)
        assert b.get_cell(5, 0) == Player.PLAYER_1

    def test_col_six_works(self, empty_board: Board) -> None:
        b = empty_board.drop_piece(6, Player.PLAYER_1)
        assert b.get_cell(5, 6) == Player.PLAYER_1

    def test_is_valid_move_boundaries(self, empty_board: Board) -> None:
        assert empty_board.is_valid_move(0) is True
        assert empty_board.is_valid_move(6) is True
