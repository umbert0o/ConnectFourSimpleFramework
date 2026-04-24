"""Tests for connect_four.game.metrics module."""

import json
import os
import tempfile

import pytest

from connect_four.game.metrics import (
    GameResult,
    MetricsTracker,
    MoveRecord,
    ResourceUsage,
)
from connect_four.game.player import Player


class TestMoveRecord:
    def test_fields_populated_correctly(self):
        record = MoveRecord(
            move_number=1,
            player=Player.PLAYER_1,
            player_move_number=1,
            column=3,
            timestamp=12345.0,
            duration=0.5,
            is_ai=True,
        )
        assert record.move_number == 1
        assert record.player == Player.PLAYER_1
        assert record.player_move_number == 1
        assert record.column == 3
        assert record.timestamp == 12345.0
        assert record.duration == 0.5
        assert record.is_ai is True

    def test_human_move_has_no_duration(self):
        record = MoveRecord(
            move_number=1,
            player=Player.PLAYER_1,
            player_move_number=1,
            column=0,
            timestamp=12345.0,
            duration=None,
            is_ai=False,
        )
        assert record.duration is None
        assert record.is_ai is False


class TestMetricsTrackerInit:
    def test_initial_state_empty(self):
        tracker = MetricsTracker("Alice", "Bob", "ai_vs_ai")
        assert len(tracker.current_game_moves) == 0
        assert len(tracker.completed_games) == 0

    def test_stores_player_names(self):
        tracker = MetricsTracker("Alpha", "Beta", "human_vs_ai")
        assert tracker.p1_name == "Alpha"
        assert tracker.p2_name == "Beta"

    def test_stores_mode(self):
        tracker = MetricsTracker("X", "Y", "human_vs_human")
        assert tracker.mode == "human_vs_human"


class TestRecordMove:
    def test_single_move_recorded(self):
        tracker = MetricsTracker("P1", "P2", "ai_vs_ai")
        tracker.start_game()
        tracker.record_move(Player.PLAYER_1, 3, duration=None, is_ai=False)
        moves = tracker.current_game_moves
        assert len(moves) == 1
        assert moves[0].column == 3
        assert moves[0].player == Player.PLAYER_1

    def test_multiple_moves_increment_numbers(self):
        tracker = MetricsTracker("P1", "P2", "ai_vs_ai")
        tracker.start_game()
        tracker.record_move(Player.PLAYER_1, 0, duration=None, is_ai=False)
        tracker.record_move(Player.PLAYER_2, 1, duration=None, is_ai=False)
        tracker.record_move(Player.PLAYER_1, 2, duration=None, is_ai=False)
        moves = tracker.current_game_moves
        assert moves[0].move_number == 1
        assert moves[1].move_number == 2
        assert moves[2].move_number == 3
        assert moves[0].player_move_number == 1
        assert moves[1].player_move_number == 1
        assert moves[2].player_move_number == 2

    def test_move_auto_timestamps(self):
        tracker = MetricsTracker("P1", "P2", "ai_vs_ai")
        tracker.start_game()
        tracker.record_move(Player.PLAYER_1, 0, duration=None, is_ai=False)
        assert tracker.current_game_moves[0].timestamp > 0

    def test_duration_none_for_human(self):
        tracker = MetricsTracker("P1", "P2", "ai_vs_ai")
        tracker.start_game()
        tracker.record_move(Player.PLAYER_1, 0, duration=None, is_ai=False)
        assert tracker.current_game_moves[0].duration is None

    def test_duration_set_for_ai(self):
        tracker = MetricsTracker("P1", "P2", "ai_vs_ai")
        tracker.start_game()
        tracker.record_move(Player.PLAYER_1, 0, duration=0.5, is_ai=True)
        assert tracker.current_game_moves[0].duration == 0.5


class TestGameLifecycle:
    def test_start_end_game(self):
        tracker = MetricsTracker("P1", "P2", "ai_vs_ai")
        tracker.start_game()
        tracker.record_move(Player.PLAYER_1, 3, duration=None, is_ai=False)
        result = tracker.end_game(Player.PLAYER_1)
        assert len(tracker.completed_games) == 1
        assert len(tracker.current_game_moves) == 0
        assert result.winner == Player.PLAYER_1

    def test_multiple_games(self):
        tracker = MetricsTracker("P1", "P2", "ai_vs_ai")
        tracker.start_game()
        tracker.record_move(Player.PLAYER_1, 0, duration=None, is_ai=False)
        tracker.end_game(Player.PLAYER_1)
        tracker.start_game()
        tracker.record_move(Player.PLAYER_2, 1, duration=None, is_ai=False)
        tracker.end_game(Player.PLAYER_2)
        assert len(tracker.completed_games) == 2

    def test_game_result_fields(self):
        tracker = MetricsTracker("Alice", "Bob", "ai_vs_ai")
        tracker.start_game()
        tracker.record_move(Player.PLAYER_1, 0, duration=0.1, is_ai=True)
        tracker.record_move(Player.PLAYER_2, 1, duration=0.2, is_ai=True)
        result = tracker.end_game(Player.PLAYER_1)
        assert result.p1_name == "Alice"
        assert result.p2_name == "Bob"
        assert result.winner == Player.PLAYER_1
        assert result.total_moves == 2
        assert result.mode == "ai_vs_ai"


class TestJsonExport:
    def test_to_json_valid_structure(self):
        tracker = MetricsTracker("A", "B", "ai_vs_ai")
        tracker.start_game()
        tracker.record_move(Player.PLAYER_1, 0, duration=0.1, is_ai=True)
        tracker.end_game(Player.PLAYER_1)
        data = json.loads(tracker.to_json())
        assert "games" in data
        assert "summary" in data

    def test_to_json_game_has_moves(self):
        tracker = MetricsTracker("A", "B", "ai_vs_ai")
        tracker.start_game()
        tracker.record_move(Player.PLAYER_1, 0, duration=0.1, is_ai=True)
        tracker.end_game(Player.PLAYER_1)
        data = json.loads(tracker.to_json())
        assert len(data["games"][0]["moves"]) == 1

    def test_save_json_creates_file(self):
        tracker = MetricsTracker("A", "B", "ai_vs_ai")
        tracker.start_game()
        tracker.record_move(Player.PLAYER_1, 0, duration=0.1, is_ai=True)
        tracker.end_game(Player.PLAYER_1)
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            tracker.save_json(path)
            assert os.path.exists(path)
            with open(path) as f:
                data = json.load(f)
            assert "games" in data
        finally:
            os.unlink(path)

    def test_json_round_trip(self):
        tracker = MetricsTracker("X", "Y", "ai_vs_ai")
        tracker.start_game()
        tracker.record_move(Player.PLAYER_1, 0, duration=0.5, is_ai=True)
        tracker.end_game(Player.PLAYER_2)
        json_str = tracker.to_json()
        data = json.loads(json_str)
        assert data["games"][0]["winner"] == Player.PLAYER_2


class TestGetSummary:
    def test_summary_keys(self):
        tracker = MetricsTracker("A", "B", "ai_vs_ai")
        summary = tracker.get_summary()
        assert "player1_wins" in summary
        assert "player2_wins" in summary
        assert "draws" in summary

    def test_summary_counts_correct(self):
        tracker = MetricsTracker("A", "B", "ai_vs_ai")
        tracker.start_game()
        tracker.record_move(Player.PLAYER_1, 0, duration=None, is_ai=False)
        tracker.end_game(Player.PLAYER_1)
        tracker.start_game()
        tracker.record_move(Player.PLAYER_2, 1, duration=None, is_ai=False)
        tracker.end_game(Player.PLAYER_2)
        tracker.start_game()
        tracker.record_move(Player.PLAYER_1, 2, duration=None, is_ai=False)
        tracker.end_game(None)
        summary = tracker.get_summary()
        assert summary["player1_wins"] == 1
        assert summary["player2_wins"] == 1
        assert summary["draws"] == 1


class TestResourceUsage:
    def test_fields_populated_correctly(self):
        ru = ResourceUsage(wall_time=1.5, peak_ram_bytes=4096)
        assert ru.wall_time == 1.5
        assert ru.peak_ram_bytes == 4096

    def test_zero_values(self):
        ru = ResourceUsage(wall_time=0.0, peak_ram_bytes=0)
        assert ru.wall_time == 0.0
        assert ru.peak_ram_bytes == 0

    def test_negative_wall_time_allowed(self):
        ru = ResourceUsage(wall_time=-0.1, peak_ram_bytes=0)
        assert ru.wall_time == -0.1


class TestGameResultResources:
    def test_resources_defaults_to_none(self):
        result = GameResult(
            game_number=1,
            winner=Player.PLAYER_1,
            total_moves=1,
            duration=1.0,
            moves=[],
            p1_name="A",
            p2_name="B",
            mode="ai_vs_ai",
        )
        assert result.resources is None

    def test_resources_set_to_dict(self):
        ru = ResourceUsage(wall_time=0.5, peak_ram_bytes=1024)
        result = GameResult(
            game_number=1,
            winner=Player.PLAYER_1,
            total_moves=1,
            duration=1.0,
            moves=[],
            p1_name="A",
            p2_name="B",
            mode="ai_vs_ai",
            resources={"player1": ru},
        )
        assert result.resources is not None
        assert result.resources["player1"].wall_time == 0.5

    def test_resources_with_both_players(self):
        result = GameResult(
            game_number=1,
            winner=Player.PLAYER_1,
            total_moves=1,
            duration=1.0,
            moves=[],
            p1_name="A",
            p2_name="B",
            mode="ai_vs_ai",
            resources={
                "player1": ResourceUsage(wall_time=1.0, peak_ram_bytes=2048),
                "player2": ResourceUsage(wall_time=0.5, peak_ram_bytes=1024),
            },
        )
        assert result.resources is not None
        assert result.resources["player1"].wall_time == 1.0
        assert result.resources["player2"].peak_ram_bytes == 1024


class TestEndGameWithResources:
    def test_end_game_without_resources(self):
        tracker = MetricsTracker("P1", "P2", "ai_vs_ai")
        tracker.start_game()
        tracker.record_move(Player.PLAYER_1, 3, duration=None, is_ai=False)
        result = tracker.end_game(Player.PLAYER_1)
        assert result.resources is None

    def test_end_game_with_resources(self):
        tracker = MetricsTracker("P1", "P2", "ai_vs_ai")
        tracker.start_game()
        tracker.record_move(Player.PLAYER_1, 3, duration=None, is_ai=False)
        result = tracker.end_game(
            Player.PLAYER_1,
            resources={"player1": ResourceUsage(wall_time=0.5, peak_ram_bytes=1024)},
        )
        assert result.resources is not None
        assert result.resources["player1"].wall_time == 0.5

    def test_end_game_with_both_player_resources(self):
        tracker = MetricsTracker("P1", "P2", "ai_vs_ai")
        tracker.start_game()
        tracker.record_move(Player.PLAYER_1, 0, duration=0.1, is_ai=True)
        tracker.record_move(Player.PLAYER_2, 1, duration=0.2, is_ai=True)
        result = tracker.end_game(
            Player.PLAYER_1,
            resources={
                "player1": ResourceUsage(wall_time=1.0, peak_ram_bytes=2048),
                "player2": ResourceUsage(wall_time=0.5, peak_ram_bytes=1024),
            },
        )
        assert result.resources is not None
        assert result.resources["player1"].wall_time == 1.0
        assert result.resources["player2"].peak_ram_bytes == 1024


class TestJsonExportWithResources:
    def test_json_includes_resources_key(self):
        tracker = MetricsTracker("A", "B", "ai_vs_ai")
        tracker.start_game()
        tracker.record_move(Player.PLAYER_1, 0, duration=0.1, is_ai=True)
        tracker.end_game(
            Player.PLAYER_1,
            resources={"player1": ResourceUsage(wall_time=0.5, peak_ram_bytes=1024)},
        )
        data = json.loads(tracker.to_json())
        assert "resources" in data["games"][0]

    def test_json_resources_has_player_keys(self):
        tracker = MetricsTracker("A", "B", "ai_vs_ai")
        tracker.start_game()
        tracker.record_move(Player.PLAYER_1, 0, duration=0.1, is_ai=True)
        tracker.end_game(
            Player.PLAYER_1,
            resources={
                "player1": ResourceUsage(wall_time=1.0, peak_ram_bytes=2048),
                "player2": ResourceUsage(wall_time=0.5, peak_ram_bytes=1024),
            },
        )
        data = json.loads(tracker.to_json())
        assert "player1" in data["games"][0]["resources"]
        assert "player2" in data["games"][0]["resources"]

    def test_json_resources_values_correct(self):
        tracker = MetricsTracker("A", "B", "ai_vs_ai")
        tracker.start_game()
        tracker.record_move(Player.PLAYER_1, 0, duration=0.1, is_ai=True)
        tracker.end_game(
            Player.PLAYER_1,
            resources={"player1": ResourceUsage(wall_time=0.5, peak_ram_bytes=1024)},
        )
        data = json.loads(tracker.to_json())
        p1 = data["games"][0]["resources"]["player1"]
        assert isinstance(p1["wall_time"], (int, float))
        assert isinstance(p1["peak_ram_bytes"], int)


class TestJsonExportWithoutResources:
    def test_json_shows_null_resources(self):
        tracker = MetricsTracker("A", "B", "ai_vs_ai")
        tracker.start_game()
        tracker.record_move(Player.PLAYER_1, 0, duration=0.1, is_ai=True)
        tracker.end_game(Player.PLAYER_1)
        data = json.loads(tracker.to_json())
        assert data["games"][0]["resources"] is None


class TestBackwardCompatibility:
    def test_existing_end_game_still_works(self):
        tracker = MetricsTracker("P1", "P2", "ai_vs_ai")
        tracker.start_game()
        tracker.record_move(Player.PLAYER_1, 3, duration=None, is_ai=False)
        result = tracker.end_game(Player.PLAYER_1)
        assert len(tracker.completed_games) == 1
        assert len(tracker.current_game_moves) == 0
        assert result.winner == Player.PLAYER_1

    def test_existing_json_export_still_works(self):
        tracker = MetricsTracker("A", "B", "ai_vs_ai")
        tracker.start_game()
        tracker.record_move(Player.PLAYER_1, 0, duration=0.1, is_ai=True)
        tracker.end_game(Player.PLAYER_1)
        data = json.loads(tracker.to_json())
        assert "games" in data
        assert "summary" in data
