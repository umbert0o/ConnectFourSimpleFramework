from __future__ import annotations
from connect_four.ai.ai_base import AIBase
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from connect_four.game.board import Board
    from connect_four.game.player import Player
    
class _MCTSNode:
    def __init__(self, state: Board, parent: _MCTSNode = None, action: int = None):
        self.state = state
        self.parent = parent
        self.action = action
        self.children: list[_MCTSNode] = []
        self.visists = 0
        self.wins = 0.0
            
    
class MctsAI(AIBase):
    def choose_move(self, board: Board, player: Player) -> int:
        return 1
    
    @property
    def name(self) -> str:
        return "MctsAI"