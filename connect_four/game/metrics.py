"""Metrics tracking for Connect Four games — pure Python, no pygame."""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass


@dataclass
class MoveRecord:
    """A single move in a game."""

    move_number: int  # Overall move number (1-based)
    player: int  # Player who made the move (Player enum value)
    player_move_number: int  # This player's Nth move (1-based)
    column: int  # Column index chosen (0-based)
    timestamp: float  # time.perf_counter() when move was recorded
    duration: float | None  # AI think time in seconds, None for human
    is_ai: bool  # Whether an AI made this move


@dataclass
class ResourceUsage:
    """Per-algorithm resource usage for a single game."""

    wall_time: float  # Sum of per-move wall-clock durations (seconds)
    peak_ram_bytes: int  # Maximum tracemalloc delta across all moves (bytes)


@dataclass
class GameResult:
    """Result of a single game."""

    game_number: int
    winner: int | None  # Player enum value, None for draw
    total_moves: int
    duration: float  # Wall-clock time
    moves: list[MoveRecord]
    p1_name: str
    p2_name: str
    mode: str  # "human_vs_human", "human_vs_ai", "ai_vs_ai"
    resources: dict[str, ResourceUsage] | None = (
        None  # Per-algorithm resources for this game
    )


class MetricsTracker:
    """Tracks moves and timing for a game or tournament."""

    def __init__(self, p1_name: str, p2_name: str, mode: str) -> None:
        self.p1_name = p1_name
        self.p2_name = p2_name
        self.mode = mode
        self._current_moves: list[MoveRecord] = []
        self._completed_games: list[GameResult] = []
        self._game_start_time: float = 0.0
        self._move_count_by_player: dict[int, int] = {1: 0, 2: 0}

    def start_game(self) -> None:
        self._current_moves = []
        self._game_start_time = time.perf_counter()
        self._move_count_by_player = {1: 0, 2: 0}

    def record_move(
        self,
        player: int,
        column: int,
        *,
        duration: float | None = None,
        is_ai: bool = False,
    ) -> None:
        self._move_count_by_player[player] = (
            self._move_count_by_player.get(player, 0) + 1
        )
        move = MoveRecord(
            move_number=len(self._current_moves) + 1,
            player=player,
            player_move_number=self._move_count_by_player[player],
            column=column,
            timestamp=time.perf_counter(),
            duration=duration,
            is_ai=is_ai,
        )
        self._current_moves.append(move)

    def end_game(
        self,
        winner: int | None,
        *,
        resources: dict[str, ResourceUsage] | None = None,
    ) -> GameResult:
        result = GameResult(
            game_number=len(self._completed_games) + 1,
            winner=winner,
            total_moves=len(self._current_moves),
            duration=time.perf_counter() - self._game_start_time,
            moves=list(self._current_moves),
            p1_name=self.p1_name,
            p2_name=self.p2_name,
            mode=self.mode,
            resources=resources,
        )
        self._completed_games.append(result)
        self._current_moves = []
        return result

    @property
    def current_game_moves(self) -> list[MoveRecord]:
        return list(self._current_moves)

    @property
    def completed_games(self) -> list[GameResult]:
        return list(self._completed_games)

    def get_summary(self) -> dict[str, int]:
        p1_wins = sum(1 for g in self._completed_games if g.winner == 1)
        p2_wins = sum(1 for g in self._completed_games if g.winner == 2)
        draws = sum(1 for g in self._completed_games if g.winner is None)
        return {
            "player1_wins": p1_wins,
            "player2_wins": p2_wins,
            "draws": draws,
        }

    def to_json(self) -> str:
        data = {
            "games": [asdict(g) for g in self._completed_games],
            "summary": self.get_summary(),
            "p1_name": self.p1_name,
            "p2_name": self.p2_name,
        }
        return json.dumps(data, indent=2)

    def save_json(self, path: str) -> None:
        with open(path, "w") as f:
            f.write(self.to_json())
