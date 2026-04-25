from __future__ import annotations

import os
import random
import time
import tracemalloc
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass

from connect_four.ai.ai_base import AIBase
from connect_four.game.game import Game
from connect_four.game.metrics import MetricsTracker, MoveRecord, ResourceUsage
from connect_four.game.player import Player
from connect_four.game.validation import validate_ai_move


@dataclass
class _SingleGameResult:
    """Picklable result of a single headless game."""

    winner: int | None
    game_number: int
    duration: float
    moves: list[MoveRecord]
    resources: dict[str, ResourceUsage]
    print_line: str


def _run_single_game(
    p1_ai: AIBase,
    p2_ai: AIBase,
    game_num: int,
    p1_name: str,
    p2_name: str,
) -> _SingleGameResult:
    """Play one complete game and return a serializable result."""
    random.seed(os.getpid() + game_num)

    game = Game()
    algo_wall_time: dict[str, float] = {"player1": 0.0, "player2": 0.0}
    algo_peak_ram: dict[str, int] = {"player1": 0, "player2": 0}
    if not tracemalloc.is_tracing():
        tracemalloc.start()
    else:
        tracemalloc.clear_traces()

    game_start = time.perf_counter()
    moves: list[MoveRecord] = []
    move_count_by_player: dict[int, int] = {1: 0, 2: 0}

    while not game.is_over:
        board = game.board
        current_player = game.current_player

        if current_player == Player.PLAYER_1:
            ai = p1_ai
        else:
            ai = p2_ai

        mem_before = tracemalloc.get_traced_memory()[0]
        start = time.perf_counter()
        col = validate_ai_move(ai, board, current_player)
        duration = time.perf_counter() - start
        mem_after = tracemalloc.get_traced_memory()[0]
        ram_delta = mem_after - mem_before
        player_key = "player1" if current_player == Player.PLAYER_1 else "player2"
        algo_wall_time[player_key] += duration
        algo_peak_ram[player_key] = max(algo_peak_ram[player_key], ram_delta)

        move_count_by_player[current_player.value] = (
            move_count_by_player.get(current_player.value, 0) + 1
        )
        moves.append(
            MoveRecord(
                move_number=len(moves) + 1,
                player=current_player.value,
                player_move_number=move_count_by_player[current_player.value],
                column=col,
                timestamp=time.perf_counter(),
                duration=duration,
                is_ai=True,
            )
        )

        game.make_move(col)

    game_duration = time.perf_counter() - game_start

    winner = game.winner
    if winner == Player.PLAYER_1:
        result_str = f"{p1_name} wins"
    elif winner == Player.PLAYER_2:
        result_str = f"{p2_name} wins"
    else:
        result_str = "Draw"

    resources = {
        "player1": ResourceUsage(
            wall_time=algo_wall_time["player1"],
            peak_ram_bytes=algo_peak_ram["player1"],
        ),
        "player2": ResourceUsage(
            wall_time=algo_wall_time["player2"],
            peak_ram_bytes=algo_peak_ram["player2"],
        ),
    }
    tracemalloc.stop()

    print_line = f"Game {game_num}: {p1_name} (P1) vs {p2_name} (P2) — {result_str}"

    return _SingleGameResult(
        winner=winner.value if winner else None,
        game_number=game_num,
        duration=game_duration,
        moves=moves,
        resources=resources,
        print_line=print_line,
    )


def run_headless(
    p1_ai: AIBase,
    p2_ai: AIBase,
    games: int = 1,
    output_path: str | None = None,
    workers: int = 1,
) -> dict[str, int]:
    """Run AI vs AI games without visual rendering.

    Args:
        p1_ai: AI controlling Player 1.
        p2_ai: AI controlling Player 2.
        games: Number of games to play.
        output_path: If set, export results as JSON to this file.
        workers: Number of parallel workers (1 = sequential).
    """
    tracker = MetricsTracker(p1_ai.name, p2_ai.name, "ai_vs_ai")
    results: dict[str, int] = {"player1_wins": 0, "player2_wins": 0, "draws": 0}

    if workers == 1:
        all_results = [
            _run_single_game(p1_ai, p2_ai, n, p1_ai.name, p2_ai.name)
            for n in range(1, games + 1)
        ]
    else:
        actual_workers = min(workers, games)
        with ProcessPoolExecutor(max_workers=actual_workers) as executor:
            future_to_num = {
                executor.submit(
                    _run_single_game, p1_ai, p2_ai, n, p1_ai.name, p2_ai.name
                ): n
                for n in range(1, games + 1)
            }
            collected: dict[int, _SingleGameResult] = {}
            for future in as_completed(future_to_num):
                num = future_to_num[future]
                collected[num] = future.result()
        all_results = [collected[n] for n in range(1, games + 1)]

    for result in all_results:
        tracker.start_game()
        for move in result.moves:
            tracker.record_move(
                move.player, move.column, duration=move.duration, is_ai=move.is_ai
            )
        tracker.end_game(result.winner, resources=result.resources)

        if result.winner == 1:
            results["player1_wins"] += 1
        elif result.winner == 2:
            results["player2_wins"] += 1
        else:
            results["draws"] += 1

        print(result.print_line)

    p1_wins = results["player1_wins"]
    p2_wins = results["player2_wins"]
    draws = results["draws"]
    print(
        f"Results after {games} games: "
        f"{p1_ai.name} won {p1_wins}, {p2_ai.name} won {p2_wins}, Draws: {draws}"
    )

    if output_path is not None:
        tracker.save_json(output_path)
        print(f"Results exported to {output_path}")

    return results
