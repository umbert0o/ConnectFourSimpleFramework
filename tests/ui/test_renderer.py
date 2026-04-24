from __future__ import annotations

import os

import pygame
import pytest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from connect_four.game.game import Game
from connect_four.game.player import Player
from connect_four.ui.renderer import HEADER_HEIGHT, PygameRenderer, _compute_dimensions


class TestComputeDimensions:
    def test_standard_board(self) -> None:
        result = _compute_dimensions(rows=6, cols=7, cell_size=100, header_height=80)
        assert result == (700, 680, 700, 600)

    def test_non_standard_board(self) -> None:
        result = _compute_dimensions(rows=5, cols=5, cell_size=80, header_height=80)
        assert result == (400, 480, 400, 400)

    def test_large_board_exceeds_max(self) -> None:
        w, h, _, _ = _compute_dimensions(
            rows=15, cols=15, cell_size=100, header_height=80
        )
        assert w > 1200 or h > 900

    def test_default_header_matches_constant(self) -> None:
        w, h, bw, bh = _compute_dimensions(6, 7, 100, HEADER_HEIGHT)
        assert h == bh + HEADER_HEIGHT
        assert w == bw

    def test_single_column(self) -> None:
        result = _compute_dimensions(rows=4, cols=1, cell_size=100, header_height=80)
        assert result == (100, 480, 100, 400)


class TestOldConstantsRemoved:
    def test_no_board_width_constant(self) -> None:
        import connect_four.ui.renderer as mod

        assert not hasattr(mod, "BOARD_WIDTH")

    def test_no_board_height_constant(self) -> None:
        import connect_four.ui.renderer as mod

        assert not hasattr(mod, "BOARD_HEIGHT")

    def test_no_window_width_constant(self) -> None:
        import connect_four.ui.renderer as mod

        assert not hasattr(mod, "WINDOW_WIDTH")

    def test_no_window_height_constant(self) -> None:
        import connect_four.ui.renderer as mod

        assert not hasattr(mod, "WINDOW_HEIGHT")

    def test_no_cell_size_constant(self) -> None:
        import connect_four.ui.renderer as mod

        assert not hasattr(mod, "CELL_SIZE")

    def test_header_height_still_exists(self) -> None:
        import connect_four.ui.renderer as mod

        assert hasattr(mod, "HEADER_HEIGHT")
        assert mod.HEADER_HEIGHT == 80


class TestDrawStatusRemoved:
    def test_no_draw_status_method(self) -> None:
        from connect_four.ui.renderer import PygameRenderer

        assert not hasattr(PygameRenderer, "_draw_status")

    def test_no_show_status_method(self) -> None:
        from connect_four.ui.renderer import PygameRenderer

        assert not hasattr(PygameRenderer, "show_status")


class TestReplayDialog:
    def _make_renderer(self) -> PygameRenderer:
        pygame.init()
        game = Game()
        return PygameRenderer(game, cell_size=80)

    def test_show_dialog_flag_default_false(self) -> None:
        renderer = self._make_renderer()
        assert renderer._show_dialog is False
        renderer.close()

    def test_clear_highlight_resets_win_cells(self) -> None:
        renderer = self._make_renderer()
        renderer._win_cells = [(0, 0), (0, 1), (0, 2), (0, 3)]
        renderer.clear_highlight()
        assert renderer._win_cells is None
        renderer.close()

    def test_draw_replay_dialog_creates_button_rects(self) -> None:
        renderer = self._make_renderer()
        renderer.draw_replay_dialog(winner=Player.PLAYER_1, is_draw=False)
        assert isinstance(renderer._replay_btn_rect, pygame.Rect)
        assert isinstance(renderer._exit_btn_rect, pygame.Rect)
        assert renderer._replay_btn_rect.width > 0
        assert renderer._replay_btn_rect.height > 0
        assert renderer._exit_btn_rect.width > 0
        assert renderer._exit_btn_rect.height > 0
        renderer.close()

    def test_draw_replay_dialog_button_positions_within_board(self) -> None:
        renderer = self._make_renderer()
        renderer.draw_replay_dialog(winner=Player.PLAYER_2, is_draw=False)
        board_width = renderer._board_width  # 7 * 80 = 560
        for rect in (renderer._replay_btn_rect, renderer._exit_btn_rect):
            assert rect is not None
            assert rect.x >= 0
            assert rect.right <= board_width
            assert rect.y > HEADER_HEIGHT
        renderer.close()
