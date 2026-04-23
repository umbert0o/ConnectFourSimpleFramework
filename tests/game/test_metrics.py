"""Tests for connect_four.game.metrics module."""

import json
import os
import tempfile

import pytest

from connect_four.game.metrics import GameResult, MetricsTracker, MoveRecord
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
