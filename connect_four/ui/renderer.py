from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from connect_four.game.board import Board
from connect_four.game.metrics import MetricsTracker
from connect_four.game.player import EMPTY, Player

if TYPE_CHECKING:
    from connect_four.game.game import Game

HEADER_HEIGHT = 80

# Info panel (right side)
PANEL_WIDTH = 280
PANEL_PADDING = 15
PANEL_BG_COLOR = (25, 25, 40)
PANEL_BORDER_COLOR = (60, 60, 80)

BG_COLOR = (30, 30, 30)
BOARD_COLOR = (0, 70, 170)
EMPTY_COLOR = (20, 20, 20)
PLAYER1_COLOR = (220, 50, 50)
PLAYER2_COLOR = (240, 220, 50)
HOVER_COLOR = (200, 200, 200)

_HIGHLIGHT_BORDER = (255, 255, 255)

_PLAYER_COLOR: dict[int, tuple[int, int, int]] = {
    Player.PLAYER_1: PLAYER1_COLOR,
    Player.PLAYER_2: PLAYER2_COLOR,
}


def _compute_dimensions(
    rows: int, cols: int, cell_size: int, header_height: int, panel_width: int = 0
) -> tuple[int, int, int, int]:
    """Return (window_width, window_height, board_width, board_height)."""
    board_width = cols * cell_size
    board_height = rows * cell_size
    window_width = board_width + panel_width
    window_height = board_height + header_height
    return window_width, window_height, board_width, board_height


class PygameRenderer:
    def __init__(self, game: Game, cell_size: int = 100) -> None:
        rows = game.board.rows
        cols = game.board.cols
        (
            self._window_width,
            self._window_height,
            self._board_width,
            self._board_height,
        ) = _compute_dimensions(rows, cols, cell_size, HEADER_HEIGHT, PANEL_WIDTH)

        if self._window_width > 1480 or self._window_height > 900:
            raise ValueError(
                f"Computed window size {self._window_width}x{self._window_height} "
                f"exceeds maximum 1480x900. Reduce cell_size."
            )

        self._cell_size = cell_size
        self._panel_width = PANEL_WIDTH
        pygame.init()
        self._game = game
        self._screen = pygame.display.set_mode(
            (self._window_width, self._window_height)
        )
        pygame.display.set_caption("Connect Four")
        self._font = pygame.font.SysFont("Arial", 32, bold=True)
        self._small_font = pygame.font.SysFont("Arial", 22)
        self._hover_col: int | None = None
        self._win_cells: list[tuple[int, int]] | None = None

        from connect_four.ui.info_panel import InfoPanel

        self._info_panel = InfoPanel(
            PANEL_WIDTH, self._board_height, self._small_font, self._small_font
        )
        self._tracker: MetricsTracker | None = None

    def render(self) -> None:
        self._screen.fill(BG_COLOR)

        board_rect = pygame.Rect(
            0, HEADER_HEIGHT, self._board_width, self._board_height
        )
        pygame.draw.rect(self._screen, BOARD_COLOR, board_rect)

        board = self._game.board
        for row in range(board.rows):
            for col in range(board.cols):
                cx = col * self._cell_size + self._cell_size // 2
                cy = HEADER_HEIGHT + row * self._cell_size + self._cell_size // 2
                cell = board.get_cell(row, col)
                color = EMPTY_COLOR if cell == EMPTY else _PLAYER_COLOR[cell]
                pygame.draw.circle(
                    self._screen, color, (cx, cy), self._cell_size // 2 - 6
                )

        if self._win_cells is not None:
            for r, c in self._win_cells:
                cx = c * self._cell_size + self._cell_size // 2
                cy = HEADER_HEIGHT + r * self._cell_size + self._cell_size // 2
                pygame.draw.circle(
                    self._screen,
                    _HIGHLIGHT_BORDER,
                    (cx, cy),
                    self._cell_size // 2 - 6,
                    5,
                )

        if self._hover_col is not None and not self._game.is_over:
            hx = self._hover_col * self._cell_size + self._cell_size // 2
            hy = HEADER_HEIGHT // 2
            disc_color = _PLAYER_COLOR[self._game.current_player]
            preview = pygame.Surface(
                (self._cell_size - 12, self._cell_size - 12), pygame.SRCALPHA
            )
            pygame.draw.circle(
                preview,
                (*disc_color, 120),
                (preview.get_width() // 2, preview.get_height() // 2),
                preview.get_width() // 2,
            )
            self._screen.blit(
                preview,
                (hx - preview.get_width() // 2, hy - preview.get_height() // 2),
            )

        if self._tracker is not None:
            self._info_panel.draw(
                self._screen,
                self._board_width,
                self._tracker,
                self._game.current_player,
                game_over=self._game.is_over,
            )

        pygame.display.flip()

    def handle_events(self) -> tuple[str, int | None]:
        """Returns ("move", col), ("quit", None), or ("none", None)."""
        mouse_x, _ = pygame.mouse.get_pos()
        # Clamp to board area
        if mouse_x >= self._board_width:
            self._hover_col = None
        else:
            self._hover_col = mouse_x // self._cell_size
        board = self._game.board
        if self._hover_col is not None and (
            self._hover_col < 0 or self._hover_col >= board.cols
        ):
            self._hover_col = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return ("quit", None)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return ("quit", None)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                col = event.pos[0] // self._cell_size
                if event.pos[0] >= self._board_width:
                    continue  # Clicked in panel area — ignore
                if 0 <= col < board.cols and board.is_valid_move(col):
                    return ("move", col)
        return ("none", None)

    def highlight_win(self, board: Board, winner: Player) -> None:
        self._win_cells = board.get_winning_cells()

    def close(self) -> None:
        pygame.quit()

    def set_tracker(self, tracker: MetricsTracker) -> None:
        self._tracker = tracker
