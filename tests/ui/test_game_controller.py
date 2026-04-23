from __future__ import annotations

import signal
import time
from unittest.mock import MagicMock

import pytest

from connect_four.ai.ai_base import AIBase
from connect_four.game.board import Board
from connect_four.game.game import Game
from connect_four.ui.game_controller import (
    VisualGameController,
    _validate_ai_move,
    _validate_ai_params,
)
from connect_four.game.player import Player
from connect_four.ui.renderer import PygameRenderer


class _StubAI(AIBase):
    def choose_move(self, board: Board, player: Player) -> int:
        return 0


class _BrokenAI(AIBase):
    def choose_move(self, board: Board, player: Player) -> int:
        return -1


class TestValidateAIParams:
    def test_ai_only_is_valid(self):
        _validate_ai_params(_StubAI(), None, None)

    def test_ai1_and_ai2_is_valid(self):
        _validate_ai_params(None, _StubAI(), _StubAI())

    def test_all_none_is_valid(self):
        _validate_ai_params(None, None, None)

    def test_ai_with_ai1_raises(self):
        with pytest.raises(ValueError, match="Cannot specify both"):
            _validate_ai_params(_StubAI(), _StubAI(), None)

    def test_ai_with_ai2_raises(self):
        with pytest.raises(ValueError, match="Cannot specify both"):
            _validate_ai_params(_StubAI(), None, _StubAI())

    def test_ai_with_both_raises(self):
        with pytest.raises(ValueError, match="Cannot specify both"):
            _validate_ai_params(_StubAI(), _StubAI(), _StubAI())

    def test_ai1_without_ai2_raises(self):
        with pytest.raises(ValueError, match="Must specify both"):
            _validate_ai_params(None, _StubAI(), None)

    def test_ai2_without_ai1_raises(self):
        with pytest.raises(ValueError, match="Must specify both"):
            _validate_ai_params(None, None, _StubAI())


class TestValidateAIMove:
    def test_valid_move_passes(self):
        ai = _StubAI()
        board = Board()
        col = _validate_ai_move(ai, board, Player.PLAYER_1)
        assert col == 0
        assert board.is_valid_move(col)

    def test_invalid_move_raises(self):
        ai = _BrokenAI()
        board = Board()
        with pytest.raises(ValueError):
            _validate_ai_move(ai, board, Player.PLAYER_1)

    def test_invalid_move_message_contains_name(self):
        ai = _BrokenAI()
        board = Board()
        with pytest.raises(ValueError, match="BrokenAI"):
            _validate_ai_move(ai, board, Player.PLAYER_1)

    def test_invalid_move_message_contains_valid_moves(self):
        ai = _BrokenAI()
        board = Board()
        with pytest.raises(ValueError, match=r"Valid moves: \["):
            _validate_ai_move(ai, board, Player.PLAYER_1)


def _make_controller(**kwargs):
    game = Game()
    renderer = MagicMock(spec=PygameRenderer)
    return VisualGameController(game, renderer, **kwargs)


class TestVisualGameController:
    def test_init_validates_params(self):
        with pytest.raises(ValueError, match="Cannot specify both"):
            _make_controller(ai=_StubAI(), ai1=_StubAI())

    def test_is_ai_turn_human_vs_ai_p2(self):
        ctrl = _make_controller(ai=_StubAI())
        assert ctrl._is_ai_turn() is False
        ctrl._game.make_move(0)
        assert ctrl._is_ai_turn() is True

    def test_is_ai_turn_human_vs_ai_p1(self):
        ctrl = _make_controller(ai=_StubAI())
        assert ctrl._is_ai_turn() is False

    def test_is_ai_turn_ai_vs_ai_p1(self):
        ctrl = _make_controller(ai1=_StubAI(), ai2=_StubAI())
        assert ctrl._is_ai_turn() is True

    def test_is_ai_turn_ai_vs_ai_p2(self):
        ctrl = _make_controller(ai1=_StubAI(), ai2=_StubAI())
        ctrl._game.make_move(0)
        assert ctrl._is_ai_turn() is True

    def test_is_ai_turn_human_vs_human(self):
        ctrl = _make_controller()
        assert ctrl._is_ai_turn() is False


class _SlowAI(AIBase):
    def choose_move(self, board: Board, player: Player) -> int:
        time.sleep(10)
        return 0


class TestTimeout:
    def test_slow_ai_raises_timeout(self):
        try:
            ctrl = _make_controller(ai=_SlowAI(), timeout_seconds=1)
            ctrl._game.make_move(0)
            with pytest.raises(TimeoutError, match="SlowAI exceeded 1"):
                ctrl._do_ai_move()
        except (OSError, ValueError):
            pytest.skip("signal handling not available in this environment")

    def test_fast_ai_completes_with_timeout(self):
        ctrl = _make_controller(ai=_StubAI(), timeout_seconds=5)
        ctrl._game.make_move(0)
        ctrl._do_ai_move()
        assert ctrl._game.board.get_cell(4, 0) == Player.PLAYER_2

    def test_timeout_seconds_stored(self):
        ctrl = _make_controller(timeout_seconds=3.5)
        assert ctrl._timeout_seconds == 3.5

    def test_timeout_default_is_none(self):
        ctrl = _make_controller()
        assert ctrl._timeout_seconds is None
