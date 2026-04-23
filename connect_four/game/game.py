from __future__ import annotations

from connect_four.game.board import Board
from connect_four.game.player import Player


class Game:
    """Pure-logic Connect Four game orchestrator.

    Manages board state, turn order, and win/draw detection.
    No rendering or input handling — pure game logic only.
    """

    def __init__(self) -> None:
        self._board: Board = Board()
        self._current_player: Player = Player.PLAYER_1
        self._winner: Player | None = None
        self._is_over: bool = False

    @property
    def current_player(self) -> Player:
        return self._current_player

    @property
    def board(self) -> Board:
        return self._board

    @property
    def is_over(self) -> bool:
        return self._is_over

    @property
    def winner(self) -> Player | None:
        return self._winner

    @property
    def is_draw(self) -> bool:
        return self._is_over and self._winner is None

    def make_move(self, col: int) -> None:
        if self._is_over:
            raise ValueError("Game is already over")

        self._board = self._board.drop_piece(col, self._current_player)

        result = self._board.check_winner()
        if result is not None:
            self._winner = Player(result)
            self._is_over = True
            return

        if self._board.is_full():
            self._is_over = True
            return

        self._current_player = (
            Player.PLAYER_2
            if self._current_player == Player.PLAYER_1
            else Player.PLAYER_1
        )

    def reset(self) -> None:
        self._board = Board()
        self._current_player = Player.PLAYER_1
        self._winner = None
        self._is_over = False

    def get_status(self) -> str:
        if self._is_over:
            if self._winner is not None:
                return f"Player {self._winner.value} wins!"
            return "Draw!"
        return f"Player {self._current_player.value}'s turn"
