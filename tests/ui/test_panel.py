"""Tests for connect_four.ui.info_panel module."""

from unittest.mock import MagicMock, patch

import pygame
import pytest

from connect_four.game.metrics import MetricsTracker
from connect_four.game.player import Player
from connect_four.ui.info_panel import InfoPanel
from connect_four.ui.renderer import PANEL_PADDING, PANEL_WIDTH, PygameRenderer


class TestInfoPanelInit:
    def test_creates_with_correct_dimensions(self):
        pygame.init()
        screen = pygame.display.set_mode((100, 100))
        font = pygame.font.SysFont("Arial", 22)
        panel = InfoPanel(280, 600, font, font)
        assert panel.width == 280
        assert panel.height == 600
        pygame.quit()


class TestInfoPanelDraw:
    def setup_method(self):
        pygame.init()
        self.screen = pygame.display.set_mode((980, 680))
        self.font = pygame.font.SysFont("Arial", 22)
        self.small_font = pygame.font.SysFont("Arial", 18)
        self.panel = InfoPanel(280, 600, self.font, self.small_font)
        self.tracker = MetricsTracker("Alice", "Bob", "ai_vs_ai")

    def test_draw_no_crash_empty_tracker(self):
        self.tracker.start_game()
        self.panel.draw(
            self.screen, 700, self.tracker, Player.PLAYER_1, game_over=False
        )

    def test_draw_no_crash_with_moves(self):
        self.tracker.start_game()
        self.tracker.record_move(Player.PLAYER_1, 3, duration=0.5, is_ai=True)
        self.tracker.record_move(Player.PLAYER_2, 4, duration=1.2, is_ai=True)
        self.tracker.record_move(Player.PLAYER_1, 5, duration=0.3, is_ai=True)
        self.panel.draw(
            self.screen, 700, self.tracker, Player.PLAYER_1, game_over=False
        )

    def test_draw_no_crash_game_over(self):
        self.tracker.start_game()
        self.tracker.record_move(Player.PLAYER_1, 3, duration=0.5, is_ai=True)
        self.tracker.end_game(Player.PLAYER_1)
        self.panel.draw(self.screen, 700, self.tracker, Player.PLAYER_1, game_over=True)

    def test_draw_game_over_no_completed_games_shows_draw(self):
        self.tracker.start_game()
        self.panel.draw(self.screen, 700, self.tracker, Player.PLAYER_1, game_over=True)


class TestRendererPanelIntegration:
    def setup_method(self):
        pygame.init()
        from connect_four.game.game import Game

        self.game = Game()
        self.renderer = PygameRenderer(self.game, cell_size=100)

    def test_renderer_window_width_with_panel(self):
        assert self.renderer._window_width == 980
        assert self.renderer._board_width == 700
        assert self.renderer._panel_width == 280

    def test_renderer_set_tracker_accepts_tracker(self):
        tracker = MetricsTracker("H", "AI", "human_vs_ai")
        self.renderer.set_tracker(tracker)

    def test_renderer_render_with_tracker_no_crash(self):
        tracker = MetricsTracker("H", "AI", "human_vs_ai")
        tracker.start_game()
        self.renderer.set_tracker(tracker)
        self.renderer.render()


class TestSectionTitleXOffset:
    def setup_method(self):
        pygame.init()
        self.font = pygame.font.SysFont("Arial", 22)
        self.small_font = pygame.font.SysFont("Arial", 18)
        self.panel = InfoPanel(280, 600, self.font, self.small_font)

    def test_blit_x_includes_x_offset(self):
        surface = MagicMock(spec=pygame.Surface)
        with patch.object(self.panel, "_font") as mock_font:
            rendered = MagicMock()
            rendered.get_height.return_value = 20
            mock_font.render.return_value = rendered
            self.panel._draw_section_title(surface, "Test Title", 10, 700)
            rendered_blit_calls = surface.blit.call_args_list
            assert len(rendered_blit_calls) == 1
            blit_pos = rendered_blit_calls[0][0][1]
            assert blit_pos[0] == 700 + PANEL_PADDING
            assert blit_pos[1] == 10

    def test_blit_x_zero_offset(self):
        surface = MagicMock(spec=pygame.Surface)
        with patch.object(self.panel, "_font") as mock_font:
            rendered = MagicMock()
            rendered.get_height.return_value = 20
            mock_font.render.return_value = rendered
            self.panel._draw_section_title(surface, "Test", 5, 0)
            blit_pos = surface.blit.call_args[0][1]
            assert blit_pos[0] == PANEL_PADDING

    def test_return_y_includes_title_height(self):
        surface = MagicMock(spec=pygame.Surface)
        with patch.object(self.panel, "_font") as mock_font:
            rendered = MagicMock()
            rendered.get_height.return_value = 24
            mock_font.render.return_value = rendered
            result_y = self.panel._draw_section_title(surface, "Test", 50, 700)
            assert result_y == 50 + 24 + 8


class TestDividerXOffset:
    def setup_method(self):
        pygame.init()
        self.font = pygame.font.SysFont("Arial", 22)
        self.small_font = pygame.font.SysFont("Arial", 18)
        self.panel = InfoPanel(280, 600, self.font, self.small_font)

    @patch("connect_four.ui.info_panel.pygame.draw.line")
    def test_line_endpoints_include_x_offset(self, mock_line):
        surface = MagicMock(spec=pygame.Surface)
        self.panel._draw_divider(surface, 100, 700)
        mock_line.assert_called_once()
        call_args = mock_line.call_args
        start_pos = call_args[0][2]
        end_pos = call_args[0][3]
        assert start_pos == (700 + PANEL_PADDING, 100)
        assert end_pos == (700 + PANEL_WIDTH - PANEL_PADDING, 100)

    @patch("connect_four.ui.info_panel.pygame.draw.line")
    def test_line_endpoints_zero_offset(self, mock_line):
        surface = MagicMock(spec=pygame.Surface)
        self.panel._draw_divider(surface, 50, 0)
        call_args = mock_line.call_args
        start_pos = call_args[0][2]
        end_pos = call_args[0][3]
        assert start_pos == (PANEL_PADDING, 50)
        assert end_pos == (PANEL_WIDTH - PANEL_PADDING, 50)

    @patch("connect_four.ui.info_panel.pygame.draw.line")
    def test_return_y_offset(self, mock_line):
        surface = MagicMock(spec=pygame.Surface)
        result_y = self.panel._draw_divider(surface, 200, 700)
        assert result_y == 200 + 8


class TestGameOverTitleRemoved:
    def setup_method(self):
        pygame.init()
        self.screen = pygame.display.set_mode((980, 680))
        self.font = pygame.font.SysFont("Arial", 22)
        self.small_font = pygame.font.SysFont("Arial", 18)
        self.panel = InfoPanel(280, 600, self.font, self.small_font)
        self.tracker = MetricsTracker("Alice", "Bob", "ai_vs_ai")

    def test_no_game_over_title_with_winner(self):
        self.tracker.start_game()
        self.tracker.record_move(Player.PLAYER_1, 3, duration=0.5, is_ai=True)
        self.tracker.end_game(Player.PLAYER_1)

        with patch.object(
            self.panel, "_draw_section_title", wraps=self.panel._draw_section_title
        ) as mock_title:
            self.panel.draw(
                self.screen, 700, self.tracker, Player.PLAYER_1, game_over=True
            )
            for c in mock_title.call_args_list:
                assert c[0][1] != "Game Over"

    def test_no_game_over_title_with_draw(self):
        self.tracker.start_game()
        self.panel.draw(self.screen, 700, self.tracker, Player.PLAYER_1, game_over=True)

        with patch.object(
            self.panel, "_draw_section_title", wraps=self.panel._draw_section_title
        ) as mock_title:
            self.panel.draw(
                self.screen, 700, self.tracker, Player.PLAYER_1, game_over=True
            )
            for c in mock_title.call_args_list:
                assert c[0][1] != "Game Over"

    @patch("connect_four.ui.info_panel.pygame.draw.line")
    def test_winner_text_still_rendered(self, _mock_line):
        self.tracker.start_game()
        self.tracker.record_move(Player.PLAYER_1, 3, duration=0.5, is_ai=True)
        self.tracker.end_game(Player.PLAYER_1)

        surface = MagicMock(spec=pygame.Surface)
        with patch.object(self.panel, "_font") as mock_font:
            rendered = MagicMock()
            rendered.get_height.return_value = 20
            mock_font.render = MagicMock(return_value=rendered)
            self.panel.draw(surface, 700, self.tracker, Player.PLAYER_1, game_over=True)
            render_calls = mock_font.render.call_args_list
            texts = [c[0][0] for c in render_calls]
            assert any("Winner: P1" in t for t in texts)

    @patch("connect_four.ui.info_panel.pygame.draw.line")
    def test_draw_text_rendered_when_no_winner(self, _mock_line):
        self.tracker.start_game()
        self.tracker.end_game(None)

        surface = MagicMock(spec=pygame.Surface)
        with patch.object(self.panel, "_font") as mock_font:
            rendered = MagicMock()
            rendered.get_height.return_value = 20
            mock_font.render = MagicMock(return_value=rendered)
            self.panel.draw(surface, 700, self.tracker, Player.PLAYER_1, game_over=True)
            render_calls = mock_font.render.call_args_list
            texts = [c[0][0] for c in render_calls]
            assert any("Draw" in t for t in texts)
