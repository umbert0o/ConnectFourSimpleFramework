from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from connect_four.board import Board
from connect_four.player import EMPTY, Player

if TYPE_CHECKING:
    from connect_four.ai_base import AIBase
    from connect_four.game import Game

CELL_SIZE = 100
BOARD_WIDTH = 700
BOARD_HEIGHT = 600
HEADER_HEIGHT = 80
WINDOW_WIDTH = BOARD_WIDTH
WINDOW_HEIGHT = BOARD_HEIGHT + HEADER_HEIGHT

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


class PygameRenderer:
    def __init__(self, game: Game) -> None:
        pygame.init()
        self._game = game
        self._screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Connect Four")
        self._font = pygame.font.SysFont("Arial", 32, bold=True)
        self._small_font = pygame.font.SysFont("Arial", 22)
        self._hover_col: int | None = None
        self._win_cells: list[tuple[int, int]] | None = None

    def render(self) -> None:
        self._screen.fill(BG_COLOR)

        self._draw_status(self._game.get_status())

        board_rect = pygame.Rect(0, HEADER_HEIGHT, BOARD_WIDTH, BOARD_HEIGHT)
        pygame.draw.rect(self._screen, BOARD_COLOR, board_rect)

        board = self._game.board
        for row in range(board.rows):
            for col in range(board.cols):
                cx = col * CELL_SIZE + CELL_SIZE // 2
                cy = HEADER_HEIGHT + row * CELL_SIZE + CELL_SIZE // 2
                cell = board.get_cell(row, col)
                color = EMPTY_COLOR if cell == EMPTY else _PLAYER_COLOR[cell]
                pygame.draw.circle(self._screen, color, (cx, cy), CELL_SIZE // 2 - 6)

        if self._win_cells is not None:
            for r, c in self._win_cells:
                cx = c * CELL_SIZE + CELL_SIZE // 2
                cy = HEADER_HEIGHT + r * CELL_SIZE + CELL_SIZE // 2
                pygame.draw.circle(
                    self._screen, _HIGHLIGHT_BORDER, (cx, cy), CELL_SIZE // 2 - 6, 5
                )

        if self._hover_col is not None and not self._game.is_over:
            hx = self._hover_col * CELL_SIZE + CELL_SIZE // 2
            hy = HEADER_HEIGHT // 2
            disc_color = _PLAYER_COLOR[self._game.current_player]
            preview = pygame.Surface((CELL_SIZE - 12, CELL_SIZE - 12), pygame.SRCALPHA)
            pygame.draw.circle(
                preview,
                (*disc_color, 120),
                (preview.get_width() // 2, preview.get_height() // 2),
                preview.get_width() // 2,
            )
            self._screen.blit(
                preview, (hx - preview.get_width() // 2, hy - preview.get_height() // 2)
            )

        pygame.display.flip()

    def handle_events(self) -> tuple[str, int | None]:
        """Returns ("move", col), ("quit", None), or ("none", None)."""
        mouse_x, _ = pygame.mouse.get_pos()
        self._hover_col = mouse_x // CELL_SIZE
        board = self._game.board
        if self._hover_col < 0 or self._hover_col >= board.cols:
            self._hover_col = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return ("quit", None)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return ("quit", None)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                col = event.pos[0] // CELL_SIZE
                if 0 <= col < board.cols and board.is_valid_move(col):
                    return ("move", col)
        return ("none", None)

    def highlight_win(self, board: Board, winner: Player) -> None:
        self._win_cells = self._find_winning_cells(board, winner)

    def show_status(self, text: str) -> None:
        self._screen.fill(BG_COLOR)
        self._draw_status(text)
        pygame.display.flip()

    def close(self) -> None:
        pygame.quit()

    def _draw_status(self, text: str) -> None:
        colour = (
            _PLAYER_COLOR[self._game.current_player]
            if not self._game.is_over and self._game.winner is None
            else (255, 255, 255)
        )
        surface = self._font.render(text, True, colour)
        x = (WINDOW_WIDTH - surface.get_width()) // 2
        y = (HEADER_HEIGHT - surface.get_height()) // 2
        self._screen.blit(surface, (x, y))

    @staticmethod
    def _find_winning_cells(board: Board, winner: Player) -> list[tuple[int, int]]:
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for r in range(board.rows):
            for c in range(board.cols):
                if board.get_cell(r, c) != winner:
                    continue
                for dr, dc in directions:
                    cells: list[tuple[int, int]] = []
                    valid = True
                    for i in range(4):
                        nr = r + dr * i
                        nc = c + dc * i
                        if nr < 0 or nr >= board.rows or nc < 0 or nc >= board.cols:
                            valid = False
                            break
                        if board.get_cell(nr, nc) != winner:
                            valid = False
                            break
                        cells.append((nr, nc))
                    if valid and len(cells) == 4:
                        return cells
        return []


def run_visual(
    game: Game,
    ai_player: AIBase | None = None,
    ai2_player: AIBase | None = None,
) -> None:
    """human-vs-AI: ai_player set, ai2_player None. Human=PLAYER_1, AI=PLAYER_2.
    AI-vs-AI: both set. Both play automatically with 0.5s delay."""
    renderer = PygameRenderer(game)

    try:
        while True:
            renderer.render()

            if game.is_over:
                if game.winner is not None:
                    renderer.highlight_win(game.board, game.winner)
                    renderer.render()
                _wait_for_exit(renderer)
                return

            if _is_ai_turn(game, ai_player, ai2_player):
                _do_ai_move(game, renderer, ai_player, ai2_player)
                continue

            action, col = renderer.handle_events()
            if action == "quit":
                return
            if action == "move" and col is not None:
                if game.board.is_valid_move(col):
                    game.make_move(col)
    finally:
        renderer.close()


def _is_ai_turn(
    game: Game,
    ai_player: AIBase | None,
    ai2_player: AIBase | None,
) -> bool:
    if ai_player is not None and game.current_player == Player.PLAYER_2:
        return True
    if ai2_player is not None and game.current_player == Player.PLAYER_1:
        return True
    return False


def _do_ai_move(
    game: Game,
    renderer: PygameRenderer,
    ai_player: AIBase | None,
    ai2_player: AIBase | None,
) -> None:
    current = game.current_player
    if current == Player.PLAYER_1 and ai2_player is not None:
        ai = ai2_player
    elif current == Player.PLAYER_2 and ai_player is not None:
        ai = ai_player
    else:
        return

    col = ai.choose_move(game.board, current)
    if game.board.is_valid_move(col):
        game.make_move(col)

    if ai_player is not None and ai2_player is not None:
        renderer.render()
        pygame.time.delay(500)


def _wait_for_exit(renderer: PygameRenderer) -> None:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                return
