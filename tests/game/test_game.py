"""Integration tests for the Game class."""

from __future__ import annotations

import pytest

from connect_four.game.board import Board
from connect_four.game.game import Game
from connect_four.game.player import EMPTY, Player


@pytest.fixture
def fresh_game() -> Game:
    return Game()


# ---------------------------------------------------------------------------
# 1. Initialisation
# ---------------------------------------------------------------------------


class TestGameInitialisation:
    def test_board_is_empty(self, fresh_game: Game) -> None:
        board = fresh_game.board
        for r in range(board.rows):
            for c in range(board.cols):
                assert board.get_cell(r, c) == EMPTY

    def test_player_1_starts(self, fresh_game: Game) -> None:
        assert fresh_game.current_player == Player.PLAYER_1

    def test_game_not_over(self, fresh_game: Game) -> None:
        assert fresh_game.is_over is False

    def test_no_winner(self, fresh_game: Game) -> None:
        assert fresh_game.winner is None

    def test_not_a_draw(self, fresh_game: Game) -> None:
        assert fresh_game.is_draw is False


# ---------------------------------------------------------------------------
# 2. Turn alternation
# ---------------------------------------------------------------------------


class TestTurnAlternation:
    def test_switches_to_player_2_after_first_move(self, fresh_game: Game) -> None:
        fresh_game.make_move(0)
        assert fresh_game.current_player == Player.PLAYER_2

    def test_switches_back_to_player_1(self, fresh_game: Game) -> None:
        fresh_game.make_move(0)
        fresh_game.make_move(1)
        assert fresh_game.current_player == Player.PLAYER_1

    def test_alternates_over_many_moves(self, fresh_game: Game) -> None:
        cols = [0, 1, 0, 1, 0]
        expected = [
            Player.PLAYER_2,
            Player.PLAYER_1,
            Player.PLAYER_2,
            Player.PLAYER_1,
            Player.PLAYER_2,
        ]
        for col, expected_player in zip(cols, expected):
            fresh_game.make_move(col)
            assert fresh_game.current_player == expected_player


# ---------------------------------------------------------------------------
# 3. Horizontal win
# ---------------------------------------------------------------------------


class TestHorizontalWin:
    def test_player_1_wins_horizontal(self, fresh_game: Game) -> None:
        for col in [0, 4, 1, 5, 2, 6]:
            fresh_game.make_move(col)
        assert fresh_game.is_over is False
        fresh_game.make_move(3)
        assert fresh_game.is_over is True
        assert fresh_game.winner == Player.PLAYER_1

    def test_turn_does_not_switch_after_win(self, fresh_game: Game) -> None:
        for col in [0, 4, 1, 5, 2, 6]:
            fresh_game.make_move(col)
        assert fresh_game.current_player == Player.PLAYER_1
        fresh_game.make_move(3)
        assert fresh_game.current_player == Player.PLAYER_1


# ---------------------------------------------------------------------------
# 4. Vertical win
# ---------------------------------------------------------------------------


class TestVerticalWin:
    def test_player_2_wins_vertical(self, fresh_game: Game) -> None:
        for col in [0, 3, 1, 3, 2, 3, 4, 3]:
            fresh_game.make_move(col)
        assert fresh_game.is_over is True
        assert fresh_game.winner == Player.PLAYER_2


# ---------------------------------------------------------------------------
# 5. Draw scenario
# ---------------------------------------------------------------------------

_DRAW_MOVES = [
    4,
    6,
    1,
    3,
    2,
    0,
    5,
    0,
    5,
    4,
    3,
    6,
    1,
    2,
    1,
    3,
    5,
    4,
    0,
    2,
    6,
    0,
    4,
    3,
    2,
    1,
    6,
    5,
    1,
    3,
    4,
    0,
    6,
    5,
    2,
    4,
    2,
    1,
    0,
    5,
    3,
    6,
]


class TestDraw:
    def test_full_board_no_winner_is_draw(self) -> None:
        game = Game()
        for col in _DRAW_MOVES:
            game.make_move(col)
        assert game.is_over is True
        assert game.winner is None
        assert game.is_draw is True


# ---------------------------------------------------------------------------
# 6. Game state consistency
# ---------------------------------------------------------------------------


class TestGameStateConsistency:
    def test_state_after_each_move(self, fresh_game: Game) -> None:
        expectations: list[tuple[int, Player, bool]] = [
            (0, Player.PLAYER_2, False),
            (3, Player.PLAYER_1, False),
            (1, Player.PLAYER_2, False),
            (3, Player.PLAYER_1, False),
            (2, Player.PLAYER_2, False),
            (3, Player.PLAYER_1, False),
            (4, Player.PLAYER_2, False),
            (3, Player.PLAYER_2, True),
        ]
        for col, expected_player, expected_over in expectations:
            fresh_game.make_move(col)
            assert fresh_game.current_player == expected_player
            assert fresh_game.is_over == expected_over
            if expected_over:
                assert fresh_game.winner == Player.PLAYER_2

    def test_board_reflects_dropped_pieces(self, fresh_game: Game) -> None:
        fresh_game.make_move(0)
        assert fresh_game.board.get_cell(5, 0) == Player.PLAYER_1.value
        fresh_game.make_move(0)
        assert fresh_game.board.get_cell(4, 0) == Player.PLAYER_2.value
        fresh_game.make_move(3)
        assert fresh_game.board.get_cell(5, 3) == Player.PLAYER_1.value


# ---------------------------------------------------------------------------
# 7. reset()
# ---------------------------------------------------------------------------


class TestReset:
    def test_reset_restores_initial_state(self, fresh_game: Game) -> None:
        for col in [0, 1, 2, 3, 4, 5]:
            fresh_game.make_move(col)
        fresh_game.reset()
        assert fresh_game.current_player == Player.PLAYER_1
        assert fresh_game.is_over is False
        assert fresh_game.winner is None
        assert fresh_game.is_draw is False
        board = fresh_game.board
        for r in range(board.rows):
            for c in range(board.cols):
                assert board.get_cell(r, c) == EMPTY

    def test_reset_after_win_allows_new_game(self, fresh_game: Game) -> None:
        for col in [0, 4, 1, 5, 2, 6, 3]:
            fresh_game.make_move(col)
        assert fresh_game.is_over is True
        fresh_game.reset()
        assert fresh_game.is_over is False
        fresh_game.make_move(0)
        assert fresh_game.current_player == Player.PLAYER_2


# ---------------------------------------------------------------------------
# 8. get_status()
# ---------------------------------------------------------------------------


class TestGetStatus:
    def test_initial_status(self, fresh_game: Game) -> None:
        assert fresh_game.get_status() == "Player 1's turn"

    def test_after_one_move(self, fresh_game: Game) -> None:
        fresh_game.make_move(0)
        assert fresh_game.get_status() == "Player 2's turn"

    def test_player_1_wins_status(self, fresh_game: Game) -> None:
        for col in [0, 4, 1, 5, 2, 6, 3]:
            fresh_game.make_move(col)
        assert fresh_game.get_status() == "Player 1 wins!"

    def test_draw_status(self) -> None:
        game = Game()
        for col in _DRAW_MOVES:
            game.make_move(col)
        assert game.get_status() == "Draw!"


# ---------------------------------------------------------------------------
# 9. Error handling — make_move after game over
# ---------------------------------------------------------------------------


class TestMakeMoveAfterGameOver:
    def test_move_after_win_raises(self, fresh_game: Game) -> None:
        for col in [0, 4, 1, 5, 2, 6, 3]:
            fresh_game.make_move(col)
        with pytest.raises(ValueError, match="Game is already over"):
            fresh_game.make_move(0)

    def test_move_after_draw_raises(self) -> None:
        game = Game()
        for col in _DRAW_MOVES:
            game.make_move(col)
        with pytest.raises(ValueError, match="Game is already over"):
            game.make_move(0)


# ---------------------------------------------------------------------------
# 10. Error handling — invalid column
# ---------------------------------------------------------------------------


class TestInvalidColumn:
    def test_negative_column_raises(self, fresh_game: Game) -> None:
        with pytest.raises(ValueError):
            fresh_game.make_move(-1)

    def test_column_out_of_range_raises(self, fresh_game: Game) -> None:
        with pytest.raises(ValueError):
            fresh_game.make_move(7)

    def test_full_column_raises(self, fresh_game: Game) -> None:
        for _ in range(6):
            fresh_game.make_move(0)
        assert fresh_game.board.is_valid_move(0) is False
        with pytest.raises(ValueError):
            fresh_game.make_move(0)


# ---------------------------------------------------------------------------
# 11. Multiple sequential games on same instance
# ---------------------------------------------------------------------------


class TestMultipleSequentialGames:
    def test_three_games_on_same_instance(self) -> None:
        game = Game()

        # Game 1: P1 horizontal win (cols 0-3 bottom row)
        for col in [0, 4, 1, 5, 2, 6, 3]:
            game.make_move(col)
        assert game.winner == Player.PLAYER_1

        game.reset()

        # Game 2: P2 vertical win in col 3
        for col in [0, 3, 1, 3, 2, 3, 4, 3]:
            game.make_move(col)
        assert game.winner == Player.PLAYER_2

        game.reset()

        # Game 3: draw
        for col in _DRAW_MOVES:
            game.make_move(col)
        assert game.is_draw is True
        assert game.winner is None
