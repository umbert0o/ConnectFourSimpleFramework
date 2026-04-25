"""Characterization tests for headless_runner and Board.get_winning_cells."""

import json

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
    def test_returns_four_cells(self, board_with_row_of_4: Board) -> None:
        cells = board_with_row_of_4.get_winning_cells()
        assert len(cells) == 4

    def test_cells_are_on_bottom_row(self, board_with_row_of_4: Board) -> None:
        cells = board_with_row_of_4.get_winning_cells()
        rows = {r for r, _ in cells}
        assert rows == {5}
        cols = {c for _, c in cells}
        assert cols == {0, 1, 2, 3}


# ---------------------------------------------------------------------------
# 6. get_winning_cells — vertical win
# ---------------------------------------------------------------------------


class TestFindWinningCellsVertical:
    def test_returns_four_cells(self, board_vertical_win: Board) -> None:
        cells = board_vertical_win.get_winning_cells()
        assert len(cells) == 4

    def test_cells_are_in_same_column(self, board_vertical_win: Board) -> None:
        cells = board_vertical_win.get_winning_cells()
        cols = {c for _, c in cells}
        assert cols == {3}
        rows = {r for r, _ in cells}
        assert rows == {2, 3, 4, 5}


# ---------------------------------------------------------------------------
# 7. get_winning_cells — diagonal win
# ---------------------------------------------------------------------------


class TestFindWinningCellsDiagonal:
    def test_returns_four_cells(self, board_diagonal_down_right: Board) -> None:
        cells = board_diagonal_down_right.get_winning_cells()
        assert len(cells) == 4

    def test_cells_form_diagonal(self, board_diagonal_down_right: Board) -> None:
        cells = board_diagonal_down_right.get_winning_cells()
        assert len(cells) == 4
        cell_set = set(cells)
        assert cell_set == {(2, 3), (3, 2), (4, 1), (5, 0)}


# ---------------------------------------------------------------------------
# 8. get_winning_cells — no winner
# ---------------------------------------------------------------------------


class TestFindWinningCellsNoWin:
    def test_empty_board_returns_empty_list(self, empty_board: Board) -> None:
        cells = empty_board.get_winning_cells()
        assert cells == []

    def test_partial_board_no_win_returns_empty_list(self) -> None:
        b = Board()
        b = b.drop_piece(0, Player.PLAYER_1)
        b = b.drop_piece(1, Player.PLAYER_2)
        b = b.drop_piece(2, Player.PLAYER_1)
        cells = b.get_winning_cells()
        assert cells == []


# ---------------------------------------------------------------------------
# 9. run_headless — output_path / JSON export
# ---------------------------------------------------------------------------


class TestOutputPath:
    def test_output_path_parameter_exists(self) -> None:
        import inspect

        sig = inspect.signature(run_headless)
        assert "output_path" in sig.parameters

    def test_json_export_creates_file(self) -> None:
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            run_headless(RandomAI(), RandomAI(), games=1, output_path=path)
            assert os.path.exists(path)
            with open(path) as f:
                data = json.load(f)
            assert "games" in data
            assert "summary" in data
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_json_export_contains_valid_game_data(self) -> None:
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            run_headless(RandomAI(), RandomAI(), games=1, output_path=path)
            with open(path) as f:
                data = json.load(f)
            assert len(data["games"]) == 1
            assert len(data["games"][0]["moves"]) > 0
            assert "p1_name" in data
            assert "p2_name" in data
        finally:
            os.unlink(path)

    def test_json_summary_matches_results(self) -> None:
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            run_headless(RandomAI(), RandomAI(), games=1, output_path=path)
            with open(path) as f:
                data = json.load(f)
            total = (
                data["summary"]["player1_wins"]
                + data["summary"]["player2_wins"]
                + data["summary"]["draws"]
            )
            assert total == 1
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# 10. run_headless — resource tracking (tracemalloc)
# ---------------------------------------------------------------------------


class TestHeadlessResources:
    """Resources dict is present in JSON output per game."""

    def test_resources_key_present_in_game_data(self) -> None:
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            run_headless(RandomAI(), RandomAI(), games=1, output_path=path)
            with open(path) as f:
                data = json.load(f)
            resources = data["games"][0]["resources"]
            assert isinstance(resources, dict)
        finally:
            if os.path.exists(path):
                os.unlink(path)


class TestHeadlessResourceTypes:
    """Resource values have correct types and are non-negative."""

    def test_player1_wall_time_is_float(self) -> None:
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            run_headless(RandomAI(), RandomAI(), games=1, output_path=path)
            with open(path) as f:
                data = json.load(f)
            p1 = data["games"][0]["resources"]["player1"]
            assert isinstance(p1["wall_time"], float)
            assert p1["wall_time"] >= 0.0
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_player1_peak_ram_bytes_is_int(self) -> None:
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            run_headless(RandomAI(), RandomAI(), games=1, output_path=path)
            with open(path) as f:
                data = json.load(f)
            p1 = data["games"][0]["resources"]["player1"]
            assert isinstance(p1["peak_ram_bytes"], int)
            assert p1["peak_ram_bytes"] >= 0
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_player2_wall_time_is_float(self) -> None:
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            run_headless(RandomAI(), RandomAI(), games=1, output_path=path)
            with open(path) as f:
                data = json.load(f)
            p2 = data["games"][0]["resources"]["player2"]
            assert isinstance(p2["wall_time"], float)
            assert p2["wall_time"] >= 0.0
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_player2_peak_ram_bytes_is_int(self) -> None:
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            run_headless(RandomAI(), RandomAI(), games=1, output_path=path)
            with open(path) as f:
                data = json.load(f)
            p2 = data["games"][0]["resources"]["player2"]
            assert isinstance(p2["peak_ram_bytes"], int)
            assert p2["peak_ram_bytes"] >= 0
        finally:
            if os.path.exists(path):
                os.unlink(path)


class TestHeadlessResourceKeys:
    """Resources dict has exactly player1 and player2 keys."""

    def test_resources_has_player1_and_player2_only(self) -> None:
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            run_headless(RandomAI(), RandomAI(), games=1, output_path=path)
            with open(path) as f:
                data = json.load(f)
            resources = data["games"][0]["resources"]
            assert set(resources.keys()) == {"player1", "player2"}
        finally:
            if os.path.exists(path):
                os.unlink(path)


class TestHeadlessResourcesMultipleGames:
    """Each game has its own independent resources dict."""

    def test_each_game_has_independent_resources(self) -> None:
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            run_headless(RandomAI(), RandomAI(), games=3, output_path=path)
            with open(path) as f:
                data = json.load(f)
            assert len(data["games"]) == 3
            # Each game must have its own resources dict
            res0 = data["games"][0]["resources"]
            res1 = data["games"][1]["resources"]
            res2 = data["games"][2]["resources"]
            # Not the same reference (independent dicts)
            assert res0 is not res1
            assert res1 is not res2
            # Each has correct keys
            for res in [res0, res1, res2]:
                assert set(res.keys()) == {"player1", "player2"}
        finally:
            if os.path.exists(path):
                os.unlink(path)


class TestHeadlessResourcesSameNameAI:
    """Resources are tracked per-player slot, not per-AI class name."""

    def test_same_ai_class_both_players(self) -> None:
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            run_headless(RandomAI(), RandomAI(), games=1, output_path=path)
            with open(path) as f:
                data = json.load(f)
            resources = data["games"][0]["resources"]
            assert "player1" in resources
            assert "player2" in resources
            # Both entries should have valid data
            assert isinstance(resources["player1"]["wall_time"], float)
            assert isinstance(resources["player2"]["wall_time"], float)
        finally:
            if os.path.exists(path):
                os.unlink(path)


# ---------------------------------------------------------------------------
# 12. run_headless — parallel execution (workers > 1)
# ---------------------------------------------------------------------------


class TestParallelExecution:
    """Parallel game execution via multiprocessing.ProcessPoolExecutor."""

    def test_workers_param_exists(self) -> None:
        """run_headless accepts a workers parameter."""
        import inspect

        sig = inspect.signature(run_headless)
        assert "workers" in sig.parameters

    def test_parallel_runs_games(self) -> None:
        """workers=2 runs games in parallel and returns correct results."""
        p1_ai = RandomAI()
        p2_ai = RandomAI()
        results = run_headless(p1_ai, p2_ai, games=4, workers=2)
        total = results["player1_wins"] + results["player2_wins"] + results["draws"]
        assert total == 4

    def test_parallel_output_json_has_correct_game_count(self) -> None:
        """Parallel execution produces JSON with all games numbered 1..N."""
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            run_headless(RandomAI(), RandomAI(), games=4, workers=2, output_path=path)
            with open(path) as f:
                data = json.load(f)
            assert len(data["games"]) == 4
            game_numbers = [g["game_number"] for g in data["games"]]
            assert game_numbers == [1, 2, 3, 4]
        finally:
            os.unlink(path)

    def test_parallel_print_output_in_order(self) -> None:
        """Parallel execution prints Game 1..N in order (buffered, not streamed)."""
        import contextlib
        import io

        p1_ai = RandomAI()
        p2_ai = RandomAI()
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            run_headless(p1_ai, p2_ai, games=4, workers=2)
        output = f.getvalue()
        lines = [line for line in output.splitlines() if line.startswith("Game ")]
        game_nums = [int(line.split(":")[0].split("Game ")[1]) for line in lines]
        assert game_nums == [1, 2, 3, 4]

    def test_parallel_resources_tracked_per_game(self) -> None:
        """Each game in parallel mode has its own resources dict."""
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            run_headless(RandomAI(), RandomAI(), games=3, workers=2, output_path=path)
            with open(path) as f:
                data = json.load(f)
            for game in data["games"]:
                assert "resources" in game
                assert "player1" in game["resources"]
                assert "player2" in game["resources"]
        finally:
            os.unlink(path)

    def test_uneven_chunk_distribution(self) -> None:
        """7 games / 3 workers distributes correctly (remainder to last chunk)."""
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            run_headless(RandomAI(), RandomAI(), games=7, workers=3, output_path=path)
            with open(path) as f:
                data = json.load(f)
            assert len(data["games"]) == 7
        finally:
            os.unlink(path)

    def test_workers_clamped_to_games_count(self) -> None:
        """When workers > games, clamp to games count."""
        p1_ai = RandomAI()
        p2_ai = RandomAI()
        results = run_headless(p1_ai, p2_ai, games=2, workers=8)
        total = results["player1_wins"] + results["player2_wins"] + results["draws"]
        assert total == 2
