from __future__ import annotations

import time
import tracemalloc

from connect_four.ai.ai_base import AIBase
from connect_four.game.game import Game
from connect_four.game.metrics import MetricsTracker, ResourceUsage
from connect_four.game.player import Player
from connect_four.game.validation import validate_ai_move


def run_headless(
    p1_ai: AIBase,
    p2_ai: AIBase,
    games: int = 1,
    output_path: str | None = None,
) -> dict[str, int]:
    """Run AI vs AI games without visual rendering.

    Args:
        p1_ai: AI controlling Player 1.
        p2_ai: AI controlling Player 2.
        games: Number of games to play.
        output_path: If set, export results as JSON to this file.
    """
    tracker = MetricsTracker(p1_ai.name, p2_ai.name, "ai_vs_ai")
    results: dict[str, int] = {"player1_wins": 0, "player2_wins": 0, "draws": 0}

    for game_num in range(1, games + 1):
        tracker.start_game()
        game = Game()

        algo_wall_time: dict[str, float] = {"player1": 0.0, "player2": 0.0}
        algo_peak_ram: dict[str, int] = {"player1": 0, "player2": 0}
        if not tracemalloc.is_tracing():
            tracemalloc.start()
        else:
            tracemalloc.clear_traces()

        while not game.is_over:
            board = game.board
            current_player = game.current_player
            valid_moves = board.get_valid_moves()

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

            game.make_move(col)
            tracker.record_move(
                current_player.value, col, duration=duration, is_ai=True
            )

        winner = game.winner
        if winner == Player.PLAYER_1:
            results["player1_wins"] += 1
            result_str = f"{p1_ai.name} wins"
        elif winner == Player.PLAYER_2:
            results["player2_wins"] += 1
            result_str = f"{p2_ai.name} wins"
        else:
            results["draws"] += 1
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
        tracker.end_game(winner.value if winner else None, resources=resources)
        tracemalloc.stop()

        print(f"Game {game_num}: {p1_ai.name} (P1) vs {p2_ai.name} (P2) — {result_str}")

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
