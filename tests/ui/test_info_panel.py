"""Tests for connect_four.ui.info_panel module."""

import os

os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame

import pytest

from connect_four.game.metrics import MetricsTracker
from connect_four.game.player import Player
from connect_four.ui.info_panel import InfoPanel
from connect_four.ui.renderer import PygameRenderer


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
