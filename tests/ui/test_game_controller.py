from __future__ import annotations

import signal
import time
from unittest.mock import MagicMock

import pytest

from connect_four.ai.ai_base import AIBase
from connect_four.game.board import Board
from connect_four.game.game import Game
from connect_four.game.player import EMPTY, Player
from connect_four.game.validation import validate_ai_move
from connect_four.ui.game_controller import VisualGameController
from connect_four.ui.renderer import PygameRenderer


class _StubAI(AIBase):
    def choose_move(self, board: Board, player: Player) -> int:
        return 0


class _BrokenAI(AIBase):
    def choose_move(self, board: Board, player: Player) -> int:
        return -1


class TestValidateAIMove:
    def test_valid_move_passes(self):
        ai = _StubAI()
        board = Board()
        col = validate_ai_move(ai, board, Player.PLAYER_1)
        assert col == 0
        assert board.is_valid_move(col)

    def test_invalid_move_raises(self):
        ai = _BrokenAI()
        board = Board()
        with pytest.raises(ValueError):
            validate_ai_move(ai, board, Player.PLAYER_1)

    def test_invalid_move_message_contains_name(self):
        ai = _BrokenAI()
        board = Board()
        with pytest.raises(ValueError, match="BrokenAI"):
            validate_ai_move(ai, board, Player.PLAYER_1)

    def test_invalid_move_message_contains_valid_moves(self):
        ai = _BrokenAI()
        board = Board()
        with pytest.raises(ValueError, match=r"Valid moves: \["):
            validate_ai_move(ai, board, Player.PLAYER_1)


def _make_controller(**kwargs):
    game = Game()
    renderer = MagicMock(spec=PygameRenderer)
    return VisualGameController(game, renderer, **kwargs)


class TestVisualGameController:
    def test_is_ai_turn_human_vs_ai_p1_human(self):
        ctrl = _make_controller(p2_ai=_StubAI())
        assert ctrl._is_ai_turn() is False
        ctrl._game.make_move(0)
        assert ctrl._is_ai_turn() is True

    def test_is_ai_turn_human_vs_ai_p1_not_ai(self):
        ctrl = _make_controller(p2_ai=_StubAI())
        assert ctrl._is_ai_turn() is False

    def test_is_ai_turn_ai_vs_ai_p1(self):
        ctrl = _make_controller(p1_ai=_StubAI(), p2_ai=_StubAI())
        assert ctrl._is_ai_turn() is True

    def test_is_ai_turn_ai_vs_ai_p2(self):
        ctrl = _make_controller(p1_ai=_StubAI(), p2_ai=_StubAI())
        ctrl._game.make_move(0)
        assert ctrl._is_ai_turn() is True

    def test_is_ai_turn_human_vs_human(self):
        ctrl = _make_controller()
        assert ctrl._is_ai_turn() is False

    def test_is_ai_turn_ai_vs_human_p1(self):
        ctrl = _make_controller(p1_ai=_StubAI())
        assert ctrl._is_ai_turn() is True
        ctrl._game.make_move(0)
        assert ctrl._is_ai_turn() is False

    def test_ai_map_both_players(self):
        stub1 = _StubAI()
        stub2 = _StubAI()
        ctrl = _make_controller(p1_ai=stub1, p2_ai=stub2)
        assert ctrl._ai_map[Player.PLAYER_1] is stub1
        assert ctrl._ai_map[Player.PLAYER_2] is stub2
        assert len(ctrl._ai_map) == 2

    def test_ai_map_p2_only(self):
        stub = _StubAI()
        ctrl = _make_controller(p2_ai=stub)
        assert Player.PLAYER_1 not in ctrl._ai_map
        assert ctrl._ai_map[Player.PLAYER_2] is stub
        assert len(ctrl._ai_map) == 1

    def test_ai_map_empty(self):
        ctrl = _make_controller()
        assert len(ctrl._ai_map) == 0


class _SlowAI(AIBase):
    def choose_move(self, board: Board, player: Player) -> int:
        time.sleep(10)
        return 0


class TestTimeout:
    def test_slow_ai_raises_timeout(self):
        try:
            ctrl = _make_controller(p2_ai=_SlowAI(), timeout_seconds=1)
            ctrl._game.make_move(0)
            with pytest.raises(TimeoutError, match="SlowAI exceeded 1"):
                ctrl._do_ai_move()
        except (OSError, ValueError):
            pytest.skip("signal handling not available in this environment")

    def test_fast_ai_completes_with_timeout(self):
        ctrl = _make_controller(p2_ai=_StubAI(), timeout_seconds=5)
        ctrl._game.make_move(0)
        ctrl._do_ai_move()
        assert ctrl._game.board.get_cell(4, 0) == Player.PLAYER_2

    def test_timeout_seconds_stored(self):
        ctrl = _make_controller(timeout_seconds=3.5)
        assert ctrl._timeout_seconds == 3.5

    def test_timeout_default_is_none(self):
        ctrl = _make_controller()
        assert ctrl._timeout_seconds is None


class TestReplayFlow:
    def test_setup_game_resets_state(self):
        ctrl = _make_controller()
        for _ in range(3):
            ctrl._game.make_move(0)
            ctrl._game.make_move(1)
        assert ctrl._game.board.get_cell(5, 0) is not None
        ctrl._game._is_over = True
        ctrl._game._winner = Player.PLAYER_1
        ctrl._game._current_player = Player.PLAYER_2

        ctrl._setup_game()

        assert ctrl._game.is_over is False
        assert ctrl._game.winner is None
        assert ctrl._game.current_player == Player.PLAYER_1
        assert ctrl._game.board.get_cell(5, 0) == EMPTY

    def test_setup_game_creates_new_tracker(self):
        ctrl = _make_controller()
        old_id = id(ctrl._tracker)
        ctrl._setup_game()
        assert id(ctrl._tracker) != old_id

    def test_setup_game_preserves_player_names(self):
        ctrl = _make_controller(p2_ai=_StubAI())
        old_p1 = ctrl._tracker.p1_name
        old_p2 = ctrl._tracker.p2_name
        old_mode = ctrl._tracker.mode

        ctrl._setup_game()

        assert ctrl._tracker.p1_name == old_p1
        assert ctrl._tracker.p2_name == old_p2
        assert ctrl._tracker.mode == old_mode

    def test_setup_game_clears_highlight(self):
        ctrl = _make_controller()
        ctrl._setup_game()
        assert ctrl._renderer.clear_highlight.called

    def test_setup_game_resets_show_dialog(self):
        ctrl = _make_controller()
        ctrl._renderer.show_dialog = True
        ctrl._setup_game()
        assert ctrl._renderer.show_dialog is False

    def test_wait_for_exit_removed(self):
        assert not hasattr(VisualGameController, "_wait_for_exit")
