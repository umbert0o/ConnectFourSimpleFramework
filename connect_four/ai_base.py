from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from connect_four.board import Board
    from connect_four.player import Player


class AIBase(ABC):
    """Abstract base class for Connect Four AI algorithms.

    Subclass this and implement choose_move() to create a custom AI.
    """

    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def choose_move(self, board: Board, player: Player) -> int:
        """Choose a column to play.

        Args:
            board: Current board state (immutable). Use drop_piece() to simulate.
            player: Which player this AI is playing as.

        Returns:
            Column index (0-6) to drop the piece into.
        """
        ...

    @property
    def name(self) -> str:
        """Human-readable name for display/logging. Override for custom names."""
        return self.__class__.__name__
