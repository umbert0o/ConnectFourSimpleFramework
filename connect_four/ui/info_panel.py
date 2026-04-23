"""Information panel rendered on the right side of the Connect Four window."""

from __future__ import annotations

import pygame

from connect_four.game.metrics import MoveRecord, MetricsTracker
from connect_four.game.player import Player
from connect_four.ui.renderer import (
    PANEL_BG_COLOR,
    PANEL_BORDER_COLOR,
    PANEL_PADDING,
    PANEL_WIDTH,
    PLAYER1_COLOR,
    PLAYER2_COLOR,
)


class InfoPanel:
    """Renders game information in the right-side panel."""

    SECTION_TITLE_COLOR = (180, 180, 200)
    TURN_P1_COLOR = PLAYER1_COLOR
    TURN_P2_COLOR = PLAYER2_COLOR
    MOVE_LOG_COLOR = (170, 170, 180)
    DIVIDER_COLOR = (60, 60, 80)

    def __init__(
        self,
        width: int,
        height: int,
        font: pygame.font.Font,
        small_font: pygame.font.Font,
    ) -> None:
        self.width = width
        self.height = height
        self._font = font
        self._small_font = small_font

    def draw(
        self,
        surface: pygame.Surface,
        x_offset: int,
        tracker: MetricsTracker,
        current_player: Player,
        game_over: bool,
    ) -> None:
        """Draw the info panel onto surface at x_offset.

        Args:
            surface: The pygame surface to draw onto.
            x_offset: Left edge of panel (equals board width).
            tracker: MetricsTracker with game data.
            current_player: Player enum for turn indicator.
            game_over: True if game has ended.
        """
        panel_rect = pygame.Rect(x_offset, 0, PANEL_WIDTH, self.height)
        surface.fill(PANEL_BG_COLOR, panel_rect)

        pygame.draw.line(
            surface, PANEL_BORDER_COLOR, (x_offset, 0), (x_offset, self.height), 1
        )

        y = PANEL_PADDING

        y = self._draw_section_title(surface, f"Mode: {tracker.mode}", y)
        p1_label = self._font.render(
            f"P1: {tracker.p1_name}", True, self.MOVE_LOG_COLOR
        )
        p2_label = self._font.render(
            f"P2: {tracker.p2_name}", True, self.MOVE_LOG_COLOR
        )
        surface.blit(p1_label, (x_offset + PANEL_PADDING, y))
        y += p1_label.get_height() + 4
        surface.blit(p2_label, (x_offset + PANEL_PADDING, y))
        y += p2_label.get_height() + 12

        if game_over:
            y = self._draw_section_title(surface, "Game Over", y)
            if tracker.completed_games:
                winner_val = tracker.completed_games[-1].winner
                winner_text = (
                    f"Winner: P{winner_val}" if winner_val is not None else "Draw"
                )
            else:
                winner_text = "Draw"
            winner_label = self._font.render(winner_text, True, (255, 255, 255))
            surface.blit(winner_label, (x_offset + PANEL_PADDING, y))
            y += winner_label.get_height() + 12
        else:
            turn_color = (
                self.TURN_P1_COLOR
                if current_player == Player.PLAYER_1
                else self.TURN_P2_COLOR
            )
            turn_indicator = pygame.Surface((16, 16), pygame.SRCALPHA)
            pygame.draw.circle(turn_indicator, (*turn_color, 255), (8, 8), 8)
            turn_text = self._font.render(
                f"Next: Player {(current_player)}", True, (255, 255, 255)
            )
            surface.blit(turn_indicator, (x_offset + PANEL_PADDING, y + 2))
            surface.blit(turn_text, (x_offset + PANEL_PADDING + 20, y))
            y += turn_text.get_height() + 12

        y = self._draw_divider(surface, y)

        y = self._draw_section_title(surface, "Move Log", y)
        moves = tracker.current_game_moves
        available_height = self.height - y - PANEL_PADDING
        self._draw_move_log(surface, moves, y, available_height, x_offset)

    def _draw_section_title(self, surface: pygame.Surface, text: str, y: int) -> int:
        title = self._font.render(text, True, self.SECTION_TITLE_COLOR)
        surface.blit(title, (PANEL_PADDING, y))
        return y + title.get_height() + 8

    def _draw_divider(self, surface: pygame.Surface, y: int) -> int:
        pygame.draw.line(
            surface,
            self.DIVIDER_COLOR,
            (PANEL_PADDING, y),
            (PANEL_WIDTH - PANEL_PADDING, y),
        )
        return y + 8

    def _draw_move_log(
        self,
        surface: pygame.Surface,
        moves: list[MoveRecord],
        y_start: int,
        available_height: int,
        x_offset: int,
    ) -> None:
        if not moves:
            empty = self._small_font.render("(no moves yet)", True, self.MOVE_LOG_COLOR)
            surface.blit(empty, (x_offset + PANEL_PADDING, y_start))
            return

        line_height = self._small_font.get_linesize()
        max_lines = max(1, int(available_height // line_height))

        visible_moves = moves[-max_lines:]
        for i, move in enumerate(visible_moves):
            if move.is_ai and move.duration is not None:
                label = f"M{move.move_number}. P{move.player} -> Col {move.column + 1} ({move.duration:.2f}s)"
            else:
                label = f"M{move.move_number}. P{move.player} -> Col {move.column + 1}"
            text = self._small_font.render(label, True, self.MOVE_LOG_COLOR)
            surface.blit(text, (x_offset + PANEL_PADDING, y_start + i * line_height))
