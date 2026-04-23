from __future__ import annotations

from connect_four.ai.ai_base import AIBase
from connect_four.game.game import Game
from connect_four.game.player import Player


def run_headless(ai1: AIBase, ai2: AIBase, games: int = 1) -> dict[str, int]:
    """Run AI vs AI games without visual rendering."""
    results: dict[str, int] = {"player1_wins": 0, "player2_wins": 0, "draws": 0}

    for game_num in range(1, games + 1):
        game = Game()

        while not game.is_over:
            board = game.board
            current_player = game.current_player
            valid_moves = board.get_valid_moves()

            if current_player == Player.PLAYER_1:
                col = ai1.choose_move(board, current_player)
            else:
                col = ai2.choose_move(board, current_player)

            if col not in valid_moves:
                raise ValueError(
                    f"AI {ai1.name if current_player == Player.PLAYER_1 else ai2.name} "
                    f"returned invalid move {col}. Valid moves: {valid_moves}"
                )

            game.make_move(col)

        winner = game.winner
        if winner == Player.PLAYER_1:
            results["player1_wins"] += 1
            result_str = f"{ai1.name} wins"
        elif winner == Player.PLAYER_2:
            results["player2_wins"] += 1
            result_str = f"{ai2.name} wins"
        else:
            results["draws"] += 1
            result_str = "Draw"

        print(f"Game {game_num}: {ai1.name} (P1) vs {ai2.name} (P2) — {result_str}")

    p1_wins = results["player1_wins"]
    p2_wins = results["player2_wins"]
    draws = results["draws"]
    print(
        f"Results after {games} games: "
        f"{ai1.name} won {p1_wins}, {ai2.name} won {p2_wins}, Draws: {draws}"
    )

    return results
