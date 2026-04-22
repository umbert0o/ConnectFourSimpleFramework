"""AI utility functions for analysing Connect Four boards.

Low-level helpers that extract windows, count pieces, measure column
heights, and score windows — building blocks for heuristic evaluation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Generator

from connect_four.player import EMPTY

if TYPE_CHECKING:
    from connect_four.board import Board


def get_all_windows(board: Board, size: int = 4) -> Generator[list[int], None, None]:
    """Yield every possible *size*-cell window on the board.

    Windows are extracted in four directions:
        horizontal  (0,  1)
        vertical    (1,  0)
        diag-right  (1,  1)
        diag-left   (1, -1)

    For a standard 6×7 board with size=4 this produces 69 windows.
    """
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    for dr, dc in directions:
        for r in range(board.rows):
            for c in range(board.cols):
                end_r = r + dr * (size - 1)
                end_c = c + dc * (size - 1)
                if end_r < 0 or end_r >= board.rows:
                    continue
                if end_c < 0 or end_c >= board.cols:
                    continue
                yield [board.get_cell(r + dr * i, c + dc * i) for i in range(size)]


def count_pieces(window: list[int], player: int) -> int:
    """Return how many cells in *window* belong to *player*."""
    return sum(1 for cell in window if cell == player)


def get_column_heights(board: Board) -> list[int]:
    """Return a list of piece counts per column (0 = empty).

    Iterates from the bottom row upward; stops at the first empty cell.
    """
    heights: list[int] = []
    for c in range(board.cols):
        count = 0
        for r in range(board.rows - 1, -1, -1):
            if board.get_cell(r, c) != EMPTY:
                count += 1
            else:
                break
        heights.append(count)
    return heights


def evaluate_window(window: list[int], player: int) -> float:
    """Score a window from *player*'s perspective.

    Returns:
        100.0  — player has all 4 pieces (win)
         10.0  — 3 of player + 1 empty (strong threat)
          3.0  — 2 of player + 2 empty (building)
        -10.0  — opponent has 3 + 1 empty (must block)
          0.0  — everything else
    """
    opponent = 3 - player
    player_count = count_pieces(window, player)
    opponent_count = count_pieces(window, opponent)
    empty_count = count_pieces(window, EMPTY)

    if player_count == 4:
        return 100.0
    if player_count == 3 and empty_count == 1:
        return 10.0
    if player_count == 2 and empty_count == 2:
        return 3.0
    if opponent_count == 3 and empty_count == 1:
        return -10.0
    return 0.0
