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


def _validate_ai_params(
    ai: AIBase | None, ai1: AIBase | None, ai2: AIBase | None
) -> None:
    """Validate AI parameter combination.

    Modes:
      - Human-vs-AI: pass ``ai`` only (plays as PLAYER_2).
      - AI-vs-AI: pass both ``ai1`` (PLAYER_1) and ``ai2`` (PLAYER_2).
      - Human-vs-Human: pass nothing.
    """
    if ai is not None and (ai1 is not None or ai2 is not None):
        raise ValueError(
            "Cannot specify both 'ai' and 'ai1'/'ai2'. "
            "Use 'ai' for human-vs-ai or 'ai1'+'ai2' for ai-vs-ai."
        )
    if ai1 is not None and ai2 is None:
        raise ValueError("Must specify both 'ai1' and 'ai2' for ai-vs-ai mode.")
    if ai2 is not None and ai1 is None:
        raise ValueError("Must specify both 'ai1' and 'ai2' for ai-vs-ai mode.")


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

    Modes:
      - Human-vs-AI: pass ``ai`` only. Human plays as PLAYER_1, AI as PLAYER_2.
      - AI-vs-AI: pass both ``ai1`` (PLAYER_1) and ``ai2`` (PLAYER_2).
        Both play automatically with 0.5s delay.
      - Human-vs-Human: pass nothing.
    """

    def __init__(
        self,
        game: Game,
        renderer: PygameRenderer,
        ai: AIBase | None = None,
        ai1: AIBase | None = None,
        ai2: AIBase | None = None,
        timeout_seconds: float | None = None,
    ) -> None:
        _validate_ai_params(ai, ai1, ai2)
        self._game = game
        self._renderer = renderer
        self._ai = ai
        self._ai1 = ai1
        self._ai2 = ai2
        self._timeout_seconds = timeout_seconds

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
        # Human-vs-AI: ai plays as PLAYER_2
        if self._ai is not None and self._game.current_player == Player.PLAYER_2:
            return True
        # AI-vs-AI: ai1 plays as PLAYER_1, ai2 plays as PLAYER_2
        if self._ai1 is not None and self._game.current_player == Player.PLAYER_1:
            return True
        if self._ai2 is not None and self._game.current_player == Player.PLAYER_2:
            return True
        return False

    def _do_ai_move(self) -> None:
        current = self._game.current_player
        # Human-vs-AI: ai plays as PLAYER_2
        if current == Player.PLAYER_2 and self._ai is not None:
            active = self._ai
        # AI-vs-AI: ai1 → PLAYER_1, ai2 → PLAYER_2
        elif current == Player.PLAYER_1 and self._ai1 is not None:
            active = self._ai1
        elif current == Player.PLAYER_2 and self._ai2 is not None:
            active = self._ai2
        else:
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

        if self._ai1 is not None and self._ai2 is not None:
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
