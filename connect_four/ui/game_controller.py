"""Visual game controller for Connect Four.

Timeout uses signal.alarm (UNIX only). On Windows, timeout is ignored.
"""

from __future__ import annotations

import signal
import time

import pygame

from connect_four.ai.ai_base import AIBase
from connect_four.game.game import Game
from connect_four.game.metrics import MetricsTracker
from connect_four.game.player import Player
from connect_four.game.validation import validate_ai_move
from connect_four.ui.renderer import PygameRenderer


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

        # Determine mode and player names for metrics
        if p1_ai is not None and p2_ai is not None:
            mode = "ai_vs_ai"
            p1_name = p1_ai.name
            p2_name = p2_ai.name
        elif p1_ai is not None:
            mode = "human_vs_ai"
            p1_name = "Human"
            p2_name = p1_ai.name
        elif p2_ai is not None:
            mode = "human_vs_ai"
            p1_name = "Human"
            p2_name = p2_ai.name
        else:
            mode = "human_vs_human"
            p1_name = "Human"
            p2_name = "Human"

        self._tracker = MetricsTracker(p1_name, p2_name, mode)
        renderer.set_tracker(self._tracker)

    def run(self) -> None:
        """Run a visual (pygame) game session with replay support."""
        try:
            while True:  # outer replay loop
                self._setup_game()
                result = self._play_game()
                if result == "exit":
                    return
        finally:
            self._renderer.close()

    def _setup_game(self) -> None:
        """Reset game state for a new game (or the first game)."""
        self._game.reset()
        self._renderer.show_dialog = False
        self._renderer.clear_highlight()
        self._tracker = MetricsTracker(
            self._tracker.p1_name, self._tracker.p2_name, self._tracker.mode
        )
        self._renderer.set_tracker(self._tracker)
        self._tracker.start_game()

    def _play_game(self) -> str:
        """Run the inner game loop. Returns 'replay' or 'exit'."""
        clock = pygame.time.Clock()
        while True:
            self._renderer.render()

            if self._game.is_over:
                if self._game.winner is not None:
                    self._tracker.end_game(self._game.winner.value)
                else:
                    self._tracker.end_game(None)
                if self._game.winner is not None:
                    self._renderer.highlight_win(self._game.board, self._game.winner)
                self._renderer.show_dialog = True
                self._renderer.render()
                while True:
                    self._renderer.render()
                    action = self._renderer.handle_dialog_events()
                    if action == "replay":
                        pygame.event.get()  # Drain stale events
                        return "replay"
                    if action == "exit":
                        return "exit"
                    clock.tick(30)

            if self._is_ai_turn():
                self._do_ai_move()
                clock.tick(60)
                continue

            action, col = self._renderer.handle_events()
            if action == "quit":
                return "exit"
            if action == "move" and col is not None:
                if self._game.board.is_valid_move(col):
                    player = self._game.current_player
                    self._game.make_move(col)
                    self._tracker.record_move(player, col, duration=None, is_ai=False)
            clock.tick(60)

    def _is_ai_turn(self) -> bool:
        return self._game.current_player in self._ai_map

    def _do_ai_move(self) -> None:
        current = self._game.current_player
        active = self._ai_map.get(current)
        if active is None:
            return

        start = time.perf_counter()

        if self._timeout_seconds is not None:

            def _handler(signum: int, frame: object) -> None:
                raise TimeoutError(
                    f"AI {active.name} exceeded {self._timeout_seconds}s time limit"
                )

            old_handler = signal.signal(signal.SIGALRM, _handler)
            signal.alarm(int(self._timeout_seconds))
            try:
                col = validate_ai_move(active, self._game.board, current)
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
        else:
            col = validate_ai_move(active, self._game.board, current)

        duration = time.perf_counter() - start
        self._game.make_move(col)
        self._tracker.record_move(current, col, duration=duration, is_ai=True)

        if len(self._ai_map) == 2:
            self._renderer.render()
            pygame.time.delay(500)
