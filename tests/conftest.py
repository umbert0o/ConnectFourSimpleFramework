"""Shared pytest fixtures for Connect Four test suite."""

import pytest

from connect_four.game.board import Board
from connect_four.game.player import Player


# ---------------------------------------------------------------------------
# Basic board fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def empty_board() -> Board:
    """Standard 6x7 empty board."""
    return Board()


@pytest.fixture
def board_with_row_of_4() -> Board:
    """Board with PLAYER_1 having a horizontal win on the bottom row (cols 0-3)."""
    b = Board()
    for c in range(4):
        b = b.drop_piece(c, Player.PLAYER_1)
    return b


# ---------------------------------------------------------------------------
# Directional win board fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def board_vertical_win() -> Board:
    """Board with PLAYER_1 having a vertical win in column 3 (rows 2-5)."""
    b = Board()
    for _ in range(4):
        b = b.drop_piece(3, Player.PLAYER_1)
    return b


@pytest.fixture
def board_diagonal_down_right() -> Board:
    """Board with PLAYER_1 having a diagonal win going down-right (dr=1, dc=1).

    Layout (bottom-up stacking in columns 0-3):
      col 0: P1                     row 5
      col 1: P2, P1                 rows 5, 4
      col 2: P2, P2, P1             rows 5, 4, 3
      col 3: P2, P2, P2, P1         rows 5, 4, 3, 2  <- P1 wins here
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


@pytest.fixture
def board_diagonal_down_left() -> Board:
    """Board with PLAYER_1 having a diagonal win going down-left (dr=1, dc=-1).

    Layout (bottom-up stacking in columns 3-6):
      col 6: P1                     row 5
      col 5: P2, P1                 rows 5, 4
      col 4: P2, P2, P1             rows 5, 4, 3
      col 3: P2, P2, P2, P1         rows 5, 4, 3, 2  <- P1 wins here
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
