"""Tests for summarize_results CLI tool — computes per-AI summary statistics from headless runner JSON output."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

# Import functions from the not-yet-existing script
# These will fail until summarize_results.py is created
from summarize_results import compute_summary, load_results, write_summary


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

FIXTURE_NORMAL = {
    "games": [
        {
            "game_number": 1,
            "winner": 1,
            "total_moves": 10,
            "moves": [
                {
                    "move_number": 1,
                    "player": 1,
                    "player_move_number": 1,
                    "column": 0,
                    "timestamp": 100.0,
                    "duration": 0.5,
                    "is_ai": True,
                },
                {
                    "move_number": 2,
                    "player": 2,
                    "player_move_number": 1,
                    "column": 1,
                    "timestamp": 100.5,
                    "duration": 0.3,
                    "is_ai": True,
                },
                {
                    "move_number": 3,
                    "player": 1,
                    "player_move_number": 2,
                    "column": 2,
                    "timestamp": 101.0,
                    "duration": 0.4,
                    "is_ai": True,
                },
                {
                    "move_number": 4,
                    "player": 2,
                    "player_move_number": 2,
                    "column": 3,
                    "timestamp": 101.5,
                    "duration": 0.6,
                    "is_ai": True,
                },
            ],
            "p1_name": "TestAI1",
            "p2_name": "TestAI2",
            "mode": "ai_vs_ai",
            "resources": {
                "player1": {"wall_time": 0.9, "peak_ram_bytes": 1000},
                "player2": {"wall_time": 0.9, "peak_ram_bytes": 2000},
            },
        },
        {
            "game_number": 2,
            "winner": 1,
            "total_moves": 8,
            "moves": [
                {
                    "move_number": 1,
                    "player": 1,
                    "player_move_number": 1,
                    "column": 0,
                    "timestamp": 200.0,
                    "duration": 0.3,
                    "is_ai": True,
                },
                {
                    "move_number": 2,
                    "player": 2,
                    "player_move_number": 1,
                    "column": 1,
                    "timestamp": 200.3,
                    "duration": 0.2,
                    "is_ai": True,
                },
            ],
            "p1_name": "TestAI1",
            "p2_name": "TestAI2",
            "mode": "ai_vs_ai",
            "resources": {
                "player1": {"wall_time": 0.3, "peak_ram_bytes": 1500},
                "player2": {"wall_time": 0.2, "peak_ram_bytes": 2500},
            },
        },
        {
            "game_number": 3,
            "winner": 2,
            "total_moves": 12,
            "moves": [
                {
                    "move_number": 1,
                    "player": 1,
                    "player_move_number": 1,
                    "column": 3,
                    "timestamp": 300.0,
                    "duration": 0.1,
                    "is_ai": True,
                },
                {
                    "move_number": 2,
                    "player": 2,
                    "player_move_number": 1,
                    "column": 4,
                    "timestamp": 300.1,
                    "duration": 0.7,
                    "is_ai": True,
                },
                {
                    "move_number": 3,
                    "player": 1,
                    "player_move_number": 2,
                    "column": 5,
                    "timestamp": 300.8,
                    "duration": 0.2,
                    "is_ai": True,
                },
                {
                    "move_number": 4,
                    "player": 2,
                    "player_move_number": 2,
                    "column": 6,
                    "timestamp": 301.0,
                    "duration": 0.4,
                    "is_ai": True,
                },
            ],
            "p1_name": "TestAI1",
            "p2_name": "TestAI2",
            "mode": "ai_vs_ai",
            "resources": {
                "player1": {"wall_time": 0.3, "peak_ram_bytes": 3000},
                "player2": {"wall_time": 1.1, "peak_ram_bytes": 3500},
            },
        },
    ],
    "summary": {"player1_wins": 2, "player2_wins": 1, "draws": 0},
    "p1_name": "TestAI1",
    "p2_name": "TestAI2",
}

FIXTURE_DRAWS = {
    "games": [
        {
            "game_number": 1,
            "winner": None,
            "total_moves": 42,
            "moves": [
                {
                    "move_number": 1,
                    "player": 1,
                    "player_move_number": 1,
                    "column": 0,
                    "timestamp": 100.0,
                    "duration": 0.5,
                    "is_ai": True,
                },
                {
                    "move_number": 2,
                    "player": 2,
                    "player_move_number": 1,
                    "column": 1,
                    "timestamp": 100.5,
                    "duration": 0.3,
                    "is_ai": True,
                },
            ],
            "p1_name": "TestAI1",
            "p2_name": "TestAI2",
            "mode": "ai_vs_ai",
            "resources": {
                "player1": {"wall_time": 0.5, "peak_ram_bytes": 1000},
                "player2": {"wall_time": 0.3, "peak_ram_bytes": 2000},
            },
        },
        {
            "game_number": 2,
            "winner": 1,
            "total_moves": 10,
            "moves": [
                {
                    "move_number": 1,
                    "player": 1,
                    "player_move_number": 1,
                    "column": 0,
                    "timestamp": 200.0,
                    "duration": 0.2,
                    "is_ai": True,
                },
            ],
            "p1_name": "TestAI1",
            "p2_name": "TestAI2",
            "mode": "ai_vs_ai",
            "resources": {
                "player1": {"wall_time": 0.2, "peak_ram_bytes": 1500},
                "player2": {"wall_time": 0.0, "peak_ram_bytes": 0},
            },
        },
    ],
    "summary": {"player1_wins": 1, "player2_wins": 0, "draws": 1},
    "p1_name": "TestAI1",
    "p2_name": "TestAI2",
}

FIXTURE_NULL_RESOURCES = {
    "games": [
        {
            "game_number": 1,
            "winner": 1,
            "total_moves": 5,
            "moves": [
                {
                    "move_number": 1,
                    "player": 1,
                    "player_move_number": 1,
                    "column": 0,
                    "timestamp": 100.0,
                    "duration": 0.5,
                    "is_ai": True,
                },
            ],
            "p1_name": "TestAI1",
            "p2_name": "TestAI2",
            "mode": "ai_vs_ai",
            "resources": None,
        },
        {
            "game_number": 2,
            "winner": 2,
            "total_moves": 6,
            "moves": [
                {
                    "move_number": 1,
                    "player": 1,
                    "player_move_number": 1,
                    "column": 0,
                    "timestamp": 200.0,
                    "duration": 0.3,
                    "is_ai": True,
                },
                {
                    "move_number": 2,
                    "player": 2,
                    "player_move_number": 1,
                    "column": 1,
                    "timestamp": 200.3,
                    "duration": 0.4,
                    "is_ai": True,
                },
            ],
            "p1_name": "TestAI1",
            "p2_name": "TestAI2",
            "mode": "ai_vs_ai",
            "resources": {
                "player1": {"wall_time": 0.3, "peak_ram_bytes": 1000},
                "player2": {"wall_time": 0.4, "peak_ram_bytes": 2000},
            },
        },
    ],
    "summary": {"player1_wins": 1, "player2_wins": 1, "draws": 0},
    "p1_name": "TestAI1",
    "p2_name": "TestAI2",
}

FIXTURE_NULL_DURATIONS = {
    "games": [
        {
            "game_number": 1,
            "winner": 1,
            "total_moves": 4,
            "moves": [
                {
                    "move_number": 1,
                    "player": 1,
                    "player_move_number": 1,
                    "column": 0,
                    "timestamp": 100.0,
                    "duration": None,
                    "is_ai": False,
                },
                {
                    "move_number": 2,
                    "player": 2,
                    "player_move_number": 1,
                    "column": 1,
                    "timestamp": 101.0,
                    "duration": 0.3,
                    "is_ai": True,
                },
                {
                    "move_number": 3,
                    "player": 1,
                    "player_move_number": 2,
                    "column": 2,
                    "timestamp": 102.0,
                    "duration": 0.5,
                    "is_ai": True,
                },
                {
                    "move_number": 4,
                    "player": 2,
                    "player_move_number": 2,
                    "column": 3,
                    "timestamp": 103.0,
                    "duration": None,
                    "is_ai": False,
                },
            ],
            "p1_name": "TestAI1",
            "p2_name": "TestAI2",
            "mode": "ai_vs_ai",
            "resources": {
                "player1": {"wall_time": 0.5, "peak_ram_bytes": 1000},
                "player2": {"wall_time": 0.3, "peak_ram_bytes": 2000},
            },
        },
    ],
    "summary": {"player1_wins": 1, "player2_wins": 0, "draws": 0},
    "p1_name": "TestAI1",
    "p2_name": "TestAI2",
}


# ---------------------------------------------------------------------------
# 1. TestComputeWinCounts
# ---------------------------------------------------------------------------


class TestComputeWinCounts:
    def test_p1_wins_counted_correctly(self) -> None:
        result = compute_summary(FIXTURE_NORMAL)
        assert result["p1_ai_wins"] == 2

    def test_p2_wins_counted_correctly(self) -> None:
        result = compute_summary(FIXTURE_NORMAL)
        assert result["p2_ai_wins"] == 1

    def test_draws_counted_correctly(self) -> None:
        result = compute_summary(FIXTURE_DRAWS)
        assert result["draws"] == 1

    def test_total_equals_game_count(self) -> None:
        result = compute_summary(FIXTURE_NORMAL)
        total = result["p1_ai_wins"] + result["p2_ai_wins"] + result["draws"]
        assert total == len(FIXTURE_NORMAL["games"])


# ---------------------------------------------------------------------------
# 2. TestComputeTurnDurations
# ---------------------------------------------------------------------------


class TestComputeTurnDurations:
    def test_p1_average_turn_duration(self) -> None:
        result = compute_summary(FIXTURE_NORMAL)
        # p1 moves: game1 [0.5, 0.4], game2 [0.3], game3 [0.1, 0.2] → [0.5, 0.4, 0.3, 0.1, 0.2] → avg 0.3
        assert result["p1_ai_data"]["average_turn_duration"] == pytest.approx(0.3)

    def test_p2_average_turn_duration(self) -> None:
        result = compute_summary(FIXTURE_NORMAL)
        # p2 moves: game1 [0.3, 0.6], game2 [0.2], game3 [0.7, 0.4] → [0.3, 0.6, 0.2, 0.7, 0.4] → avg 0.44
        assert result["p2_ai_data"]["average_turn_duration"] == pytest.approx(0.44)

    def test_null_durations_excluded_from_average(self) -> None:
        result = compute_summary(FIXTURE_NULL_DURATIONS)
        # p1 moves: [None, 0.5] → only 0.5 counted → avg 0.5
        assert result["p1_ai_data"]["average_turn_duration"] == pytest.approx(0.5)

    def test_all_null_durations_returns_none(self) -> None:
        data = {
            "games": [
                {
                    "game_number": 1,
                    "winner": 1,
                    "total_moves": 2,
                    "moves": [
                        {
                            "move_number": 1,
                            "player": 1,
                            "player_move_number": 1,
                            "column": 0,
                            "timestamp": 100.0,
                            "duration": None,
                            "is_ai": True,
                        },
                        {
                            "move_number": 2,
                            "player": 2,
                            "player_move_number": 1,
                            "column": 1,
                            "timestamp": 101.0,
                            "duration": 0.3,
                            "is_ai": True,
                        },
                    ],
                    "p1_name": "A",
                    "p2_name": "B",
                    "mode": "ai_vs_ai",
                    "resources": None,
                },
            ],
            "summary": {"player1_wins": 1, "player2_wins": 0, "draws": 0},
            "p1_name": "A",
            "p2_name": "B",
        }
        result = compute_summary(data)
        assert result["p1_ai_data"]["average_turn_duration"] is None


# ---------------------------------------------------------------------------
# 3. TestComputeResourceStats
# ---------------------------------------------------------------------------


class TestComputeResourceStats:
    def test_p1_average_wall_time(self) -> None:
        result = compute_summary(FIXTURE_NORMAL)
        # p1 wall_times: [0.9, 0.3, 0.3] → avg 0.5
        assert result["p1_ai_data"]["average_wall_time"] == pytest.approx(0.5)

    def test_p2_average_wall_time(self) -> None:
        result = compute_summary(FIXTURE_NORMAL)
        # p2 wall_times: [0.9, 0.2, 1.1] → avg ≈ 0.7333
        assert result["p2_ai_data"]["average_wall_time"] == pytest.approx(
            0.7333, abs=0.01
        )

    def test_p1_ram_stats(self) -> None:
        result = compute_summary(FIXTURE_NORMAL)
        # p1 peak_ram_bytes: [1000, 1500, 3000] → avg≈1833.33, max=3000, min=1000
        assert result["p1_ai_data"]["average_peak_ram_bytes"] == pytest.approx(
            1833.33, abs=0.01
        )
        assert result["p1_ai_data"]["maximum_peak_ram_bytes"] == 3000
        assert result["p1_ai_data"]["minimum_peak_ram_bytes"] == 1000

    def test_p2_ram_stats(self) -> None:
        result = compute_summary(FIXTURE_NORMAL)
        # p2 peak_ram_bytes: [2000, 2500, 3500] → avg≈2666.67, max=3500, min=2000
        assert result["p2_ai_data"]["average_peak_ram_bytes"] == pytest.approx(
            2666.67, abs=0.01
        )
        assert result["p2_ai_data"]["maximum_peak_ram_bytes"] == 3500
        assert result["p2_ai_data"]["minimum_peak_ram_bytes"] == 2000


# ---------------------------------------------------------------------------
# 4. TestComputeNullResources
# ---------------------------------------------------------------------------


class TestComputeNullResources:
    def test_null_resources_skipped(self) -> None:
        result = compute_summary(FIXTURE_NULL_RESOURCES)
        # Only game 2 has resources: p1 wall_time=0.3, p2 wall_time=0.4
        assert result["p1_ai_data"]["average_wall_time"] == pytest.approx(0.3)
        assert result["p2_ai_data"]["average_wall_time"] == pytest.approx(0.4)

    def test_ram_stats_with_null_resources(self) -> None:
        result = compute_summary(FIXTURE_NULL_RESOURCES)
        # Only game 2: p1 ram=1000, p2 ram=2000 → avg=max=min for both
        assert result["p1_ai_data"]["average_peak_ram_bytes"] == 1000
        assert result["p1_ai_data"]["maximum_peak_ram_bytes"] == 1000
        assert result["p1_ai_data"]["minimum_peak_ram_bytes"] == 1000
        assert result["p2_ai_data"]["average_peak_ram_bytes"] == 2000
        assert result["p2_ai_data"]["maximum_peak_ram_bytes"] == 2000
        assert result["p2_ai_data"]["minimum_peak_ram_bytes"] == 2000


# ---------------------------------------------------------------------------
# 5. TestComputeMode
# ---------------------------------------------------------------------------


class TestComputeMode:
    def test_mode_extracted_from_games(self) -> None:
        result = compute_summary(FIXTURE_NORMAL)
        assert result["mode"] == "ai_vs_ai"

    def test_games_count(self) -> None:
        result = compute_summary(FIXTURE_NORMAL)
        assert result["games"] == len(FIXTURE_NORMAL["games"])


# ---------------------------------------------------------------------------
# 6. TestCLIErrors
# ---------------------------------------------------------------------------


class TestCLIErrors:
    def test_nonexistent_file_exits_1(self) -> None:
        proc = subprocess.run(
            [sys.executable, "summarize_results.py", "/no/such/file.json"],
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 1

    def test_invalid_json_exits_1(self, tmp_path: Path) -> None:
        bad_json = tmp_path / "bad.json"
        bad_json.write_text("not valid json {{{")
        proc = subprocess.run(
            [sys.executable, "summarize_results.py", str(bad_json)],
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 1

    def test_missing_games_key_exits_1(self, tmp_path: Path) -> None:
        no_games = tmp_path / "no_games.json"
        no_games.write_text("{}")
        proc = subprocess.run(
            [sys.executable, "summarize_results.py", str(no_games)],
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 1


# ---------------------------------------------------------------------------
# 7. TestCLIOutput
# ---------------------------------------------------------------------------


class TestCLIOutput:
    def _run_cli(
        self, input_path: Path, tmp_path: Path
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "summarize_results.py", str(input_path)],
            capture_output=True,
            text=True,
            cwd=str(tmp_path),
        )

    def test_output_file_created_with_correct_name(self, tmp_path: Path) -> None:
        input_file = tmp_path / "results.json"
        input_file.write_text(json.dumps(FIXTURE_NORMAL))
        proc = self._run_cli(input_file, tmp_path)
        assert proc.returncode == 0
        expected_output = tmp_path / "results_summary.json"
        assert expected_output.exists()

    def test_output_json_has_correct_keys(self, tmp_path: Path) -> None:
        input_file = tmp_path / "results.json"
        input_file.write_text(json.dumps(FIXTURE_NORMAL))
        self._run_cli(input_file, tmp_path)
        output_file = tmp_path / "results_summary.json"
        data = json.loads(output_file.read_text())
        expected_keys = {
            "games",
            "mode",
            "p1_ai_name",
            "p2_ai_name",
            "p1_ai_wins",
            "p2_ai_wins",
            "draws",
            "p1_ai_data",
            "p2_ai_data",
        }
        assert expected_keys.issubset(set(data.keys()))
        expected_ai_data_keys = {
            "average_turn_duration",
            "average_wall_time",
            "average_peak_ram_bytes",
            "maximum_peak_ram_bytes",
            "minimum_peak_ram_bytes",
        }
        assert expected_ai_data_keys.issubset(set(data["p1_ai_data"].keys()))
        assert expected_ai_data_keys.issubset(set(data["p2_ai_data"].keys()))

    def test_output_values_correct(self, tmp_path: Path) -> None:
        input_file = tmp_path / "results.json"
        input_file.write_text(json.dumps(FIXTURE_NORMAL))
        self._run_cli(input_file, tmp_path)
        output_file = tmp_path / "results_summary.json"
        data = json.loads(output_file.read_text())
        assert data["games"] == 3
        assert data["p1_ai_wins"] == 2
        assert data["p2_ai_wins"] == 1
        assert data["draws"] == 0
        assert data["mode"] == "ai_vs_ai"
        assert data["p1_ai_name"] == "TestAI1"
        assert data["p2_ai_name"] == "TestAI2"
