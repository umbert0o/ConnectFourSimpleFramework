"""Characterization tests for headless_runner and Board.get_winning_cells."""

import pytest

from connect_four.ai.ai_base import AIBase
from connect_four.ai.random_ai import RandomAI
from connect_four.game.board import Board
from connect_four.game.player import Player
from connect_four.headless_runner import run_headless


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class BrokenAI(AIBase):
    """AI that always returns an invalid column (-1)."""

    def choose_move(self, board: Board, player: Player) -> int:
        return -1

    @property
    def name(self) -> str:
        return "BrokenAI"


# ---------------------------------------------------------------------------
# 1. run_headless — result structure
# ---------------------------------------------------------------------------


class TestRunHeadlessStructure:
    def test_results_dict_keys(self) -> None:
        p1_ai = RandomAI()
        p2_ai = RandomAI()
        results = run_headless(p1_ai, p2_ai, games=1)
        assert set(results.keys()) == {"player1_wins", "player2_wins", "draws"}

    def test_results_values_sum_to_games_count(self) -> None:
        p1_ai = RandomAI()
        p2_ai = RandomAI()
        results = run_headless(p1_ai, p2_ai, games=1)
        assert results["player1_wins"] + results["player2_wins"] + results["draws"] == 1

    def test_results_values_are_non_negative(self) -> None:
        p1_ai = RandomAI()
        p2_ai = RandomAI()
        results = run_headless(p1_ai, p2_ai, games=1)
        assert results["player1_wins"] >= 0
        assert results["player2_wins"] >= 0
        assert results["draws"] >= 0


# ---------------------------------------------------------------------------
# 2. run_headless — invalid AI move
# ---------------------------------------------------------------------------


class TestRunHeadlessInvalidMove:
    def test_broken_ai_raises_value_error(self) -> None:
        p1_ai = BrokenAI()
        p2_ai = RandomAI()
        with pytest.raises(ValueError, match="returned invalid move -1"):
            run_headless(p1_ai, p2_ai, games=1)

    def test_error_message_contains_ai_name(self) -> None:
        p1_ai = BrokenAI()
        p2_ai = RandomAI()
        with pytest.raises(ValueError, match="BrokenAI"):
            run_headless(p1_ai, p2_ai, games=1)


# ---------------------------------------------------------------------------
# 3. run_headless — multiple games
# ---------------------------------------------------------------------------


class TestRunHeadlessMultipleGames:
    def test_three_games_sum_to_three(self) -> None:
        p1_ai = RandomAI()
        p2_ai = RandomAI()
        results = run_headless(p1_ai, p2_ai, games=3)
        total = results["player1_wins"] + results["player2_wins"] + results["draws"]
        assert total == 3


# ---------------------------------------------------------------------------
# 4. run_headless — stdout output
# ---------------------------------------------------------------------------


class TestRunHeadlessStdout:
    def test_single_game_prints_game_result(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        p1_ai = RandomAI()
        p2_ai = RandomAI()
        run_headless(p1_ai, p2_ai, games=1)
        captured = capsys.readouterr()
        assert "Game 1:" in captured.out
        assert "RandomAI (P1)" in captured.out
        assert "RandomAI (P2)" in captured.out

    def test_prints_summary_line(self, capsys: pytest.CaptureFixture[str]) -> None:
        p1_ai = RandomAI()
        p2_ai = RandomAI()
        run_headless(p1_ai, p2_ai, games=1)
        captured = capsys.readouterr()
        assert "Results after 1 games:" in captured.out


# ---------------------------------------------------------------------------
# 5. get_winning_cells — horizontal win
# ---------------------------------------------------------------------------


class TestFindWinningCellsHorizontal:
    def _build_horizontal_win(self) -> Board:
        b = Board()
        for c in range(4):
            b = b.drop_piece(c, Player.PLAYER_1)
        return b

    def test_returns_four_cells(self) -> None:
        board = self._build_horizontal_win()
        cells = board.get_winning_cells()
        assert len(cells) == 4

    def test_cells_are_on_bottom_row(self) -> None:
        board = self._build_horizontal_win()
        cells = board.get_winning_cells()
        rows = {r for r, _ in cells}
        assert rows == {5}
        cols = {c for _, c in cells}
        assert cols == {0, 1, 2, 3}


# ---------------------------------------------------------------------------
# 6. get_winning_cells — vertical win
# ---------------------------------------------------------------------------


class TestFindWinningCellsVertical:
    def _build_vertical_win(self) -> Board:
        b = Board()
        for _ in range(4):
            b = b.drop_piece(3, Player.PLAYER_1)
        return b

    def test_returns_four_cells(self) -> None:
        board = self._build_vertical_win()
        cells = board.get_winning_cells()
        assert len(cells) == 4

    def test_cells_are_in_same_column(self) -> None:
        board = self._build_vertical_win()
        cells = board.get_winning_cells()
        cols = {c for _, c in cells}
        assert cols == {3}
        rows = {r for r, _ in cells}
        assert rows == {2, 3, 4, 5}


# ---------------------------------------------------------------------------
# 7. get_winning_cells — diagonal win
# ---------------------------------------------------------------------------


class TestFindWinningCellsDiagonal:
    def _build_diagonal_down_right(self) -> Board:
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

    def test_returns_four_cells(self) -> None:
        board = self._build_diagonal_down_right()
        cells = board.get_winning_cells()
        assert len(cells) == 4

    def test_cells_form_diagonal(self) -> None:
        board = self._build_diagonal_down_right()
        cells = board.get_winning_cells()
        assert len(cells) == 4
        cell_set = set(cells)
        assert cell_set == {(2, 3), (3, 2), (4, 1), (5, 0)}


# ---------------------------------------------------------------------------
# 8. get_winning_cells — no winner
# ---------------------------------------------------------------------------


class TestFindWinningCellsNoWin:
    def test_empty_board_returns_empty_list(self) -> None:
        board = Board()
        cells = board.get_winning_cells()
        assert cells == []

    def test_partial_board_no_win_returns_empty_list(self) -> None:
        b = Board()
        b = b.drop_piece(0, Player.PLAYER_1)
        b = b.drop_piece(1, Player.PLAYER_2)
        b = b.drop_piece(2, Player.PLAYER_1)
        cells = b.get_winning_cells()
        assert cells == []
