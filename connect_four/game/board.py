from __future__ import annotations

from connect_four.game.player import EMPTY, Player


class Board:
    """Immutable Connect Four game board.

    Row 0 is the top, pieces fall downward (gravity).
    Cell values: 0 = empty, 1 = PLAYER_1, 2 = PLAYER_2.
    """

    def __init__(
        self,
        rows: int = 6,
        cols: int = 7,
        _grid: tuple[tuple[int, ...], ...] | None = None,
    ) -> None:
        self._rows = rows
        self._cols = cols
        if _grid is not None:
            self._grid = _grid
        else:
            self._grid = tuple(tuple(EMPTY for _ in range(cols)) for _ in range(rows))

    @property
    def rows(self) -> int:
        return self._rows

    @property
    def cols(self) -> int:
        return self._cols

    def get_cell(self, row: int, col: int) -> int:
        return self._grid[row][col]

    def is_valid_move(self, col: int) -> bool:
        if col < 0 or col >= self._cols:
            return False
        return self._grid[0][col] == EMPTY

    def get_valid_moves(self) -> list[int]:
        return [c for c in range(self._cols) if self.is_valid_move(c)]

    def is_full(self) -> bool:
        return len(self.get_valid_moves()) == 0

    def drop_piece(self, col: int, player: Player) -> Board:
        if col < 0 or col >= self._cols:
            raise ValueError(f"Column {col} is out of range")
        if self._grid[0][col] != EMPTY:
            raise ValueError(f"Column {col} is full")

        target_row = -1
        for r in range(self._rows - 1, -1, -1):
            if self._grid[r][col] == EMPTY:
                target_row = r
                break

        new_rows: list[tuple[int, ...]] = []
        for r in range(self._rows):
            if r == target_row:
                new_rows.append(
                    tuple(
                        player if c == col else self._grid[r][c]
                        for c in range(self._cols)
                    )
                )
            else:
                new_rows.append(self._grid[r])

        return Board(self._rows, self._cols, tuple(new_rows))

    def check_winner(self) -> Player | None:
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for r in range(self._rows):
            for c in range(self._cols):
                player = self._grid[r][c]
                if player == EMPTY:
                    continue
                for dr, dc in directions:
                    if self._check_line(r, c, dr, dc, player):
                        return player
        return None

    def get_winning_cells(self) -> list[tuple[int, int]]:
        """Return the 4 cells forming the winning line, or [] if no winner."""
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for r in range(self._rows):
            for c in range(self._cols):
                player = self._grid[r][c]
                if player == EMPTY:
                    continue
                for dr, dc in directions:
                    cells: list[tuple[int, int]] = []
                    valid = True
                    for i in range(4):
                        ri = r + dr * i
                        ci = c + dc * i
                        if ri < 0 or ri >= self._rows or ci < 0 or ci >= self._cols:
                            valid = False
                            break
                        if self._grid[ri][ci] != player:
                            valid = False
                            break
                        cells.append((ri, ci))
                    if valid and len(cells) == 4:
                        return cells
        return []

    def _check_line(self, row: int, col: int, dr: int, dc: int, player: Player) -> bool:
        for i in range(4):
            r = row + dr * i
            c = col + dc * i
            if r < 0 or r >= self._rows or c < 0 or c >= self._cols:
                return False
            if self._grid[r][c] != player:
                return False
        return True

    def __str__(self) -> str:
        lines: list[str] = []
        for row in self._grid:
            lines.append(" ".join(str(cell) for cell in row))
        lines.append("-" * (self._cols * 2 - 1))
        lines.append(" ".join(str(c) for c in range(self._cols)))
        return "\n".join(lines)
