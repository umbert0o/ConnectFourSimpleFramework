from __future__ import annotations
import math
import random
from typing import TYPE_CHECKING

from connect_four.ai.ai_base import AIBase

if TYPE_CHECKING:
    from connect_four.game.board import Board
    from connect_four.game.player import Player


class _MCTSNode:
    """Represents a single state in the search tree."""
    def __init__(self, state: Board, parent: _MCTSNode | None = None, 
                 action: int | None = None, current_player: Player | None = None):
        self.state = state
        self.parent = parent
        self.action = action
        self.current_player = current_player
        self.children: list[_MCTSNode] = []
        self.visits = 0
        self.wins = 0.0
        self.unexplored_moves = list(state.get_valid_moves())

    def uct_value(self, exploration_weight: float) -> float:
        """Upper Confidence Bound for Trees formula."""
        if self.visits == 0:
            return float('inf')
        exploitation = self.wins / self.visits
        exploration = exploration_weight * math.sqrt(math.log(self.parent.visits) / self.visits)
        return exploitation + exploration


class MCTSAI(AIBase):
    """Monte Carlo Tree Search AI for Connect Four."""
    
    def __init__(self, iterations: int = 1000, exploration_weight: float = 1.41, **kwargs):
        super().__init__(**kwargs)
        self._iterations = iterations
        self._exploration_weight = exploration_weight

    def choose_move(self, board: Board, player: Player) -> int:
        root = _MCTSNode(state=board, current_player=player)
        self._root_player = player

        for _ in range(self._iterations):
            # 1. Selection
            node = root
            while not node.unexplored_moves and node.children:
                node = max(node.children, key=lambda c: c.uct_value(self._exploration_weight))

            # 2. Expansion
            if node.unexplored_moves and not node.state.check_winner() and not node.state.is_full():
                action = random.choice(node.unexplored_moves)
                node.unexplored_moves.remove(action)
                child_state = node.state.drop_piece(action, node.current_player)
                next_player = Player.PLAYER_2 if node.current_player == Player.PLAYER_1 else Player.PLAYER_1
                child = _MCTSNode(state=child_state, parent=node, action=action, current_player=next_player)
                node.children.append(child)
                node = child

            # 3. Simulation
            result = self._simulate(node.state, node.current_player)

            # 4. Backpropagation
            self._backpropagate(node, result)

        # Return the move with the highest visit count (most robust)
        if not root.children:
            return random.choice(root.unexplored_moves)
        return max(root.children, key=lambda c: c.visits).action

    def _simulate(self, state: Board, current_player: Player) -> float:
        """Random playout until terminal state. Returns +1.0 (root win), -1.0 (root loss), 0.0 (draw)."""
        curr = current_player
        while True:
            winner = state.check_winner()
            if winner is not None:
                return 1.0 if winner == self._root_player else -1.0
            if state.is_full():
                return 0.0
            col = random.choice(state.get_valid_moves())
            state = state.drop_piece(col, curr)
            curr = Player.PLAYER_2 if curr == Player.PLAYER_1 else Player.PLAYER_1

    def _backpropagate(self, node: _MCTSNode, result: float):
        """Propagate result up the tree, flipping perspective at each level for zero-sum tracking."""
        while node is not None:
            node.visits += 1
            node.wins += result
            result = -result  # Flip sign because players alternate turns
            node = node.parent

    @property
    def name(self) -> str:
        return "MctsAI"