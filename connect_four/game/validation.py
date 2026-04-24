"""AI move validation — consolidated in one place."""

from __future__ import annotations

from connect_four.ai.ai_base import AIBase
from connect_four.game.board import Board
from connect_four.game.player import Player


def validate_ai_move(ai: AIBase, board: Board, player: Player) -> int:
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
