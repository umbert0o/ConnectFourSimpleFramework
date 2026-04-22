from __future__ import annotations

import random
from typing import TYPE_CHECKING

from connect_four.ai_base import AIBase

if TYPE_CHECKING:
    from connect_four.board import Board
    from connect_four.player import Player


class RandomAI(AIBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def choose_move(self, board: Board, player: Player) -> int:
        return random.choice(board.get_valid_moves())

    @property
    def name(self) -> str:
        return "RandomAI"
