"""Tests for the public API exposed via connect_four.__init__."""

import sys


def test_public_api_imports():
    """Every name in __all__ must be importable from the top-level package."""
    import connect_four

    for name in connect_four.__all__:
        assert hasattr(connect_four, name), f"{name!r} missing from connect_four"


def test_existing_import_paths_still_work():
    """Submodule-level imports must remain functional via sub-package paths."""
    from connect_four.ai.ai_base import AIBase
    from connect_four.game.board import Board
    from connect_four.ai.board_helpers import (
        count_pieces,
        evaluate_window,
        get_all_windows,
        get_column_heights,
    )
    from connect_four.game.game import Game
    from connect_four.game.player import EMPTY, Player
    from connect_four.ai.random_ai import RandomAI

    assert AIBase is not None
    assert Board is not None
    assert Player is not None
    assert Game is not None
    assert RandomAI is not None
    assert EMPTY == 0
    assert callable(get_all_windows)
    assert callable(count_pieces)
    assert callable(get_column_heights)
    assert callable(evaluate_window)


def test_no_pygame_import():
    """Importing the package must NOT pull in pygame (breaks headless/CI)."""
    if "pygame" in sys.modules:
        del sys.modules["pygame"]
    if "connect_four" in sys.modules:
        del sys.modules["connect_four"]

    import connect_four  # noqa: F401 — re-import after clearing cache

    assert "pygame" not in sys.modules
