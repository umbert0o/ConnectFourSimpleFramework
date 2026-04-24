# Connect Four Framework

A Python framework for implementing, testing, and benchmarking Connect Four AI algorithms. Comes with a built-in pygame GUI for interactive play and a headless runner for automated tournaments with resource tracking.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Dependencies: `pygame>=2.5.0`, `pytest>=7.0`. Requires Python 3.10+.

## Running a Game

### Human vs Human

```bash
python -m connect_four
```

Opens a pygame window. Click a column to drop your piece. Player 1 is red, Player 2 is yellow. Press **Escape** to quit.

### Human vs AI

```bash
python -m connect_four --p1-ai connect_four.ai.random_ai.RandomAI
```

Player 1 is controlled by `RandomAI`, Player 2 is human. Swap to `--p2-ai` to have the AI play as Player 2 instead.

### AI vs AI (Visual)

```bash
python -m connect_four \
  --p1-ai connect_four.ai.random_ai.RandomAI \
  --p2-ai connect_four.ai.mcts_ai.MctsAI
```

Both players are AI-controlled in the pygame window with a 500ms delay between moves so you can follow the action.

### AI vs AI (Headless)

No display needed. Great for running many games and collecting metrics.

```bash
python -m connect_four --headless \
  --p1-ai connect_four.ai.random_ai.RandomAI \
  --p2-ai connect_four.ai.mcts_ai.MctsAI \
  --games 100 \
  --output results.json
```

Output during the run:

```
Game 1: RandomAI (P1) vs MctsAI (P2) — RandomAI wins
Game 2: RandomAI (P1) vs MctsAI (P2) — MctsAI wins
...
Results after 100 games: RandomAI won 52, MctsAI won 40, Draws: 8
Results exported to results.json
```

## CLI Reference

| Flag | Default | Description |
|------|---------|-------------|
| `--p1-ai <path>` | *(none, human)* | Dotted path to AI class for Player 1 |
| `--p2-ai <path>` | *(none, human)* | Dotted path to AI class for Player 2 |
| `--p1-ai-params <key=value> ...` | *(none)* | Constructor parameters for P1 AI |
| `--p2-ai-params <key=value> ...` | *(none)* | Constructor parameters for P2 AI |
| `--headless` | `false` | Run without pygame window (requires both `--p1-ai` and `--p2-ai`) |
| `--games <n>` | `1` | Number of games in headless mode |
| `--output <path>` | *(none)* | Export headless results to JSON |
| `--timeout <seconds>` | *(none)* | Per-move timeout for AI (UNIX only) |

### AI Path Format

AI classes are specified as **dotted module paths**, not file paths:

```bash
# Correct
--p1-ai connect_four.ai.random_ai.RandomAI

# Wrong — this is a file path, not a module path
--p1-ai connect_four/ai/random_ai.py::RandomAI
```

### Passing AI Parameters

Constructor arguments are passed as `key=value` pairs. Values are auto-typed:

| Value | Type |
|-------|------|
| `42` | `int` |
| `3.14` | `float` |
| `true` / `false` | `bool` |
| `hello` | `str` |

```bash
python -m connect_four --headless \
  --p1-ai connect_four.ai.mcts_ai.MctsAI --p1-ai-params iterations=500 \
  --p2-ai connect_four.ai.random_ai.RandomAI \
  --games 10 --output results.json
```

## Headless Output Format

When using `--output`, the JSON file contains:

```json
{
  "games": [
    {
      "game_number": 1,
      "winner": 1,
      "total_moves": 23,
      "duration": 0.142,
      "moves": [
        {
          "move_number": 1,
          "player": 1,
          "player_move_number": 1,
          "column": 3,
          "timestamp": 72410.123,
          "duration": 0.0001,
          "is_ai": true
        }
      ],
      "p1_name": "RandomAI",
      "p2_name": "MctsAI",
      "mode": "ai_vs_ai",
      "resources": {
        "player1": { "wall_time": 0.042, "peak_ram_bytes": 2048 },
        "player2": { "wall_time": 0.098, "peak_ram_bytes": 4096 }
      }
    }
  ],
  "summary": { "player1_wins": 6, "player2_wins": 3, "draws": 1 },
  "p1_name": "RandomAI",
  "p2_name": "MctsAI"
}
```

Each game records per-move timing, the full move log, and resource usage (wall-clock time and peak RAM delta via `tracemalloc`) for each algorithm.

## Writing Your Own AI

Subclass `AIBase` and implement `choose_move`:

```python
# connect_four/ai/my_ai.py
from __future__ import annotations
from connect_four.ai.ai_base import AIBase
from connect_four.game.board import Board
from connect_four.game.player import Player


class MyAI(AIBase):
    def __init__(self, depth: int = 4, **kwargs):
        self._depth = depth

    def choose_move(self, board: Board, player: Player) -> int:
        # Return a column index (0-6)
        for col in board.get_valid_moves():
            simulated = board.drop_piece(col, player)
            if simulated.check_winner() == player:
                return col
        return board.get_valid_moves()[0]

    @property
    def name(self) -> str:
        return "MyAI"
```

Run it:

```bash
python -m connect_four --headless \
  --p1-ai connect_four.ai.my_ai.MyAI --p1-ai-params depth=6 \
  --p2-ai connect_four.ai.random_ai.RandomAI \
  --games 50 --output my_results.json
```

### AI Contract

- Your `choose_move(board, player)` must return an **integer column index (0-6)** that is a valid move.
- The framework validates every AI move. Returning an invalid column raises `ValueError`.
- Accept `**kwargs` in `__init__` to ignore unexpected parameters from the CLI.
- Override the `name` property for readable output in logs and results.
- The `board` is **immutable** — use `board.drop_piece(col, player)` to simulate moves (returns a new `Board`).

### Available Board API

| Method | Description |
|--------|-------------|
| `board.get_valid_moves()` | `list[int]` — columns that aren't full |
| `board.is_valid_move(col)` | `bool` — check a specific column |
| `board.drop_piece(col, player)` | `Board` — new board state after a move |
| `board.check_winner()` | `Player | None` — check for a winner |
| `board.get_cell(row, col)` | `int` — cell value (0=empty, 1=P1, 2=P2) |
| `board.is_full()` | `bool` — no valid moves left |
| `board.rows` / `board.cols` | Board dimensions (default 6×7) |

### Board Helpers

Import from `connect_four.ai.board_helpers`:

| Function | Description |
|----------|-------------|
| `get_all_windows(board, size=4)` | All possible windows (horizontal, vertical, both diagonals). 69 windows on a 6×7 board with size 4. |
| `evaluate_window(window, player)` | Score a 4-cell window from a player's perspective. Returns `100.0` (win), `10.0` (3+1 empty), `3.0` (2+2 empty), `-10.0` (opponent 3+1), or `0.0`. |
| `count_pieces(window, player)` | Count how many cells belong to a player in a window. |
| `get_column_heights(board)` | `list[int]` — piece count per column (0 = empty column). |

### Included AIs

| AI | Class | Description |
|----|-------|-------------|
| Random | `connect_four.ai.random_ai.RandomAI` | Picks a random valid column. Good baseline. |
| MCTS | `connect_four.ai.mcts_ai.MctsAI` | Monte Carlo Tree Search. Accepts `iterations` parameter (default 1000). |

## Visual Game Controls

| Control | Action |
|---------|--------|
| **Mouse click** on a column | Drop a piece |
| **Escape** | Quit |
| **Play Again** button | Start a new game (after game over) |
| **Exit** button | Close the window |

The right panel shows the current game mode, player names, turn indicator, and a scrollable move log (AI moves show think time).

## Running Tests

```bash
pytest                      # all tests
pytest tests/game/          # board, game logic, metrics
pytest tests/ai/            # AI interface, board helpers
pytest tests/ui/            # renderer, panel, game controller
pytest tests/test_cli.py    # CLI parsing and AI loading
pytest tests/test_headless_runner.py  # headless runner and JSON export
pytest tests/test_public_api.py       # import contracts
pytest -k "test_name"      # single test by name
```

## Project Structure

```
connect_four/
├── __init__.py            # Public API (no pygame imports)
├── __main__.py            # Entry point
├── cli.py                 # CLI with argparse, dynamic AI class loading
├── headless_runner.py     # AI-vs-AI runner with resource tracking
├── game/                  # Pure game logic (no pygame dependency)
│   ├── board.py           # Immutable Board
│   ├── game.py            # Game orchestrator
│   ├── player.py          # Player IntEnum
│   ├── validation.py      # AI move validation
│   └── metrics.py         # Move tracking, JSON export
├── ai/                    # AI implementations
│   ├── ai_base.py         # AIBase abstract class
│   ├── random_ai.py       # Random baseline
│   ├── mcts_ai.py         # Monte Carlo Tree Search
│   └── board_helpers.py   # Window extraction, heuristic scoring
└── ui/                    # Pygame visual layer
    ├── renderer.py        # Board rendering, hover preview, win highlight
    ├── game_controller.py # Event loop, AI turns, replay
    ├── info_panel.py      # Right-side info panel
    └── constants.py       # Colors, dimensions
```
