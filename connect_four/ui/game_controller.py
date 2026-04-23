"""Visual game controller for Connect Four.

Timeout uses signal.alarm (UNIX only). On Windows, timeout is ignored.
"""

from __future__ import annotations

import signal

import pygame

from connect_four.ai.ai_base import AIBase
from connect_four.game.board import Board
from connect_four.game.game import Game
from connect_four.game.player import Player
from connect_four.ui.renderer import PygameRenderer


def _validate_ai_move(ai: AIBase, board: Board, player: Player) -> int:
    """Call *ai* and validate the returned column.

    Returns the column on success.  Raises :class:`ValueError` when the AI
    returns a column that is not in the board's current valid moves.
    """
    col = ai.choose_move(board, player)
    if not board.is_valid_move(col):
        raise ValueError(
            f"AI {ai.name} returned invalid move {col} for player {player}. "
            f"Valid moves: {board.get_valid_moves()}"
        )
    return col


class VisualGameController:
    """Orchestrates a visual (pygame) game session.

    Args:
        game: Game instance.
        renderer: PygameRenderer instance.
        p1_ai: Optional AI for Player 1. If None, P1 is human-controlled.
        p2_ai: Optional AI for Player 2. If None, P2 is human-controlled.
        timeout_seconds: Optional per-move timeout (UNIX only).
    """

    def __init__(
        self,
        game: Game,
        renderer: PygameRenderer,
        p1_ai: AIBase | None = None,
        p2_ai: AIBase | None = None,
        timeout_seconds: float | None = None,
    ) -> None:
        self._game = game
        self._renderer = renderer
        self._p1_ai = p1_ai
        self._p2_ai = p2_ai
        self._timeout_seconds = timeout_seconds
        self._ai_map: dict[Player, AIBase] = {}
        if p1_ai is not None:
            self._ai_map[Player.PLAYER_1] = p1_ai
        if p2_ai is not None:
            self._ai_map[Player.PLAYER_2] = p2_ai

    def run(self) -> None:
        """Run a visual (pygame) game session."""
        clock = pygame.time.Clock()
        try:
            while True:
                self._renderer.render()

                if self._game.is_over:
                    if self._game.winner is not None:
                        self._renderer.highlight_win(
                            self._game.board, self._game.winner
                        )
                        self._renderer.render()
                    self._wait_for_exit()
                    return

                if self._is_ai_turn():
                    self._do_ai_move()
                    clock.tick(60)
                    continue

                action, col = self._renderer.handle_events()
                if action == "quit":
                    return
                if action == "move" and col is not None:
                    if self._game.board.is_valid_move(col):
                        self._game.make_move(col)
                clock.tick(60)
        finally:
            self._renderer.close()

    def _is_ai_turn(self) -> bool:
        return self._game.current_player in self._ai_map

    def _do_ai_move(self) -> None:
        current = self._game.current_player
        active = self._ai_map.get(current)
        if active is None:
            return

        if self._timeout_seconds is not None:

            def _handler(signum: int, frame: object) -> None:
                raise TimeoutError(
                    f"AI {active.name} exceeded {self._timeout_seconds}s time limit"
                )

            old_handler = signal.signal(signal.SIGALRM, _handler)
            signal.alarm(int(self._timeout_seconds))
            try:
                col = _validate_ai_move(active, self._game.board, current)
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
        else:
            col = _validate_ai_move(active, self._game.board, current)

        self._game.make_move(col)

        if len(self._ai_map) == 2:
            self._renderer.render()
            pygame.time.delay(500)

    def _wait_for_exit(self) -> None:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    return
            pygame.time.Clock().tick(30)
