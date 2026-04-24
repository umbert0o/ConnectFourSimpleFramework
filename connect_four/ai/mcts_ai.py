from __future__ import annotations
import math
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
        self.unexplored_moves = list(state.get_valid_moves())
        
    def uct_value(self, exploration_weight: float = 1.41) -> float:
        if self.visists == 0:
            return float('inf')
        exploitation = self.wins / self.visists
        exploration = exploration_weight * math.sqrt(math.log(self.parent.visists) / self.visists)
        return exploitation + exploration
    
class MctsAI(AIBase):
    def __init__(self, iterations: int = 1000):
        self._iterations = iterations
    
    def choose_move(self, board: Board, player: Player) -> int:
        return 1
    
    @property
    def name(self) -> str:
        return "MctsAI"