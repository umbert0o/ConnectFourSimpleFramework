# Connect Four Framework

A Python framework for implementing and testing Connect Four AI algorithms. No `setup.py` / `pyproject.toml` — install deps manually.

## Setup

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Dependencies: `pygame>=2.5.0`, `pytest>=7.0`.

## Running

```bash
# Visual game (human vs human)
python -m connect_four

# AI vs AI headless (no pygame window needed)
python -m connect_four --headless --p1-ai connect_four.ai.random_ai.RandomAI --p2-ai connect_four.ai.mcts_ai.MctsAI

# AI with constructor params
python -m connect_four --headless --p1-ai connect_four.ai.mcts_ai.MctsAI --p1-ai-params iterations=500 --p2-ai connect_four.ai.random_ai.RandomAI --games 10 --output results.json

# Visual with one AI player
python -m connect_four --p1-ai connect_four.ai.random_ai.RandomAI
```

CLI AI paths use **dotted module paths** (`module.ClassName`), not file paths. Params are `key=value` pairs auto-typed (int, float, bool, string).

## Tests

```bash
pytest                          # all tests
pytest tests/game/              # single sub-package
pytest tests/test_cli.py        # single file
pytest -k "test_public_api"     # single test by name
```

Config: `pytest.ini` sets `testpaths = tests`. No custom markers or conftest plugins beyond fixtures.

### Test structure mirrors source

- `tests/game/` — board, game logic, metrics
- `tests/ai/` — AI interface, board helpers
- `tests/ui/` — renderer, panel, game controller (pygame; may need display)
- `tests/test_cli.py` — CLI parsing and AI class loading
- `tests/test_headless_runner.py` — headless runner, JSON export, resource tracking
- `tests/test_public_api.py` — import contracts and **no-pygame-import guarantee**

### Key test constraint

`test_no_pygame_import` verifies that `import connect_four` does **not** pull in pygame. This is critical for CI/headless environments. Keep the top-level `__init__.py` free of UI imports.

## Architecture

```
connect_four/
├── __init__.py          # Public API (re-exports from sub-packages, NO pygame)
├── __main__.py          # Entry point → cli.main()
├── cli.py               # argparse CLI, dynamic AI class loading
├── headless_runner.py   # AI-vs-AI without pygame, tracemalloc resource tracking
├── game/                # Pure logic — no UI, no pygame dependency
│   ├── board.py         # Immutable Board (tuple-of-tuples), gravity, win detection
│   ├── game.py          # Turn management, Game orchestrator
│   ├── player.py        # Player IntEnum (PLAYER_1=1, PLAYER_2=2), EMPTY=0
│   ├── validation.py    # AI move validation wrapper
│   └── metrics.py       # MetricsTracker, MoveRecord, ResourceUsage, JSON export
├── ai/                  # AI implementations
│   ├── ai_base.py       # AIBase ABC — subclass this to add AIs
│   ├── random_ai.py     # RandomAI baseline
│   ├── mcts_ai.py       # MctsAI (stub — choose_move returns hardcoded 1)
│   └── board_helpers.py # Window extraction, column heights, heuristic scoring
└── ui/                  # Pygame visual layer (lazy-imported, not in public API)
    ├── renderer.py      # PygameRenderer — drawing, hover, win highlight, replay dialog
    ├── game_controller.py  # VisualGameController — event loop, AI timeout (UNIX only)
    ├── info_panel.py    # Right-side info panel (mode, turn, move log)
    └── constants.py     # Colors, dimensions, panel sizing
```

### Key design decisions

- **Board is immutable** — `drop_piece()` returns a new `Board`. Never mutate in place.
- **Row 0 = top, gravity pulls down.** Column indices 0–6.
- **AI contract**: subclass `AIBase`, implement `choose_move(board, player) → int` (column 0–6). Accept `**kwargs` in `__init__`.
- **Timeout uses `signal.alarm`** (UNIX only) — ignored on Windows.
- **`validate_ai_move`** wraps every AI call — raises `ValueError` if the AI returns an invalid column. Tests for `BrokenAI` verify this.

### Extending with a new AI

1. Create `connect_four/ai/my_ai.py`
2. Subclass `AIBase`, implement `choose_move(board, player) → int`
3. Optional: override `name` property for display
4. Run via CLI: `python -m connect_four --p1-ai connect_four.ai.my_ai.MyAI`

## Style notes

- Python 3.10+ syntax (`X | None`, no `Optional`)
- `from __future__ import annotations` in most files
- No linter/formatter config in repo — follow existing patterns in the file you're editing
- Tests use plain `pytest` (no `unittest`), class-based grouping by feature
