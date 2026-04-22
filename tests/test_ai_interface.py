"""Contract tests for the AI interface (AIBase and its subclasses)."""

from __future__ import annotations

import pytest

from connect_four.ai_base import AIBase
from connect_four.board import Board
from connect_four.player import Player
from connect_four.random_ai import RandomAI


# ---------------------------------------------------------------------------
# 1. AIBase is abstract
# ---------------------------------------------------------------------------


class TestAIBaseAbstract:
    def test_cannot_instantiate_aibase(self) -> None:
        with pytest.raises(TypeError):
            AIBase()  # type: ignore[abstract]

    def test_subclass_without_choose_move_raises_typeerror(self) -> None:
        class IncompleteAI(AIBase):
            pass

        with pytest.raises(TypeError):
            IncompleteAI()  # type: ignore[abstract]

    def test_subclass_with_choose_move_instantiates(self) -> None:
        class MinimalAI(AIBase):
            def choose_move(self, board: Board, player: Player) -> int:
                return 0

        ai = MinimalAI()
        assert isinstance(ai, AIBase)


# ---------------------------------------------------------------------------
# 2. AIBase.name property
# ---------------------------------------------------------------------------


class TestAIBaseName:
    def test_default_name_returns_class_name(self) -> None:
        class MyAI(AIBase):
            def choose_move(self, board: Board, player: Player) -> int:
                return 0

        ai = MyAI()
        assert ai.name == "MyAI"

    def test_name_can_be_overridden(self) -> None:
        class CustomNameAI(AIBase):
            @property
            def name(self) -> str:
                return "Super AI 3000"

            def choose_move(self, board: Board, player: Player) -> int:
                return 0

        ai = CustomNameAI()
        assert ai.name == "Super AI 3000"


# ---------------------------------------------------------------------------
# 3. AIBase.__init__ accepts **kwargs
# ---------------------------------------------------------------------------


class TestAIBaseInit:
    def test_init_accepts_kwargs(self) -> None:
        class KwargsAI(AIBase):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.config = kwargs

            def choose_move(self, board: Board, player: Player) -> int:
                return 0

        ai = KwargsAI(depth=4, seed=42)
        assert ai.config == {"depth": 4, "seed": 42}

    def test_init_no_kwargs(self) -> None:
        class SimpleAI(AIBase):
            def choose_move(self, board: Board, player: Player) -> int:
                return 0

        ai = SimpleAI()
        assert isinstance(ai, AIBase)


# ---------------------------------------------------------------------------
# 4. Custom subclass with **kwargs config
# ---------------------------------------------------------------------------


class TestCustomSubclass:
    def test_custom_subclass_uses_config(self) -> None:
        class ConfigurableAI(AIBase):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.preferred_col: int = kwargs.get("preferred_col", 0)

            def choose_move(self, board: Board, player: Player) -> int:
                if board.is_valid_move(self.preferred_col):
                    return self.preferred_col
                return board.get_valid_moves()[0]

        ai = ConfigurableAI(preferred_col=3)
        board = Board()
        move = ai.choose_move(board, Player.PLAYER_1)
        assert move == 3


# ---------------------------------------------------------------------------
# 5. RandomAI contract
# ---------------------------------------------------------------------------


class TestRandomAIContract:
    def test_randomai_is_aibase_subclass(self) -> None:
        assert issubclass(RandomAI, AIBase)
        ai = RandomAI()
        assert isinstance(ai, AIBase)

    def test_randomai_choose_move_returns_valid_column(self) -> None:
        board = Board()
        ai = RandomAI()
        for _ in range(20):
            col = ai.choose_move(board, Player.PLAYER_1)
            assert isinstance(col, int)
            assert 0 <= col < board.cols
            assert board.is_valid_move(col)

    def test_randomai_nearly_full_board(self) -> None:
        """Only column 3 has a single empty slot left."""
        board = Board()
        # Fill all columns except col 3 completely (6 rows each)
        for col in range(board.cols):
            if col == 3:
                continue
            for _ in range(board.rows):
                board = board.drop_piece(col, Player.PLAYER_1)

        # Fill col 3 except one slot (top row should be empty)
        for _ in range(board.rows - 1):
            board = board.drop_piece(3, Player.PLAYER_2)

        # Only column 3 should be valid
        assert board.get_valid_moves() == [3]

        ai = RandomAI()
        col = ai.choose_move(board, Player.PLAYER_1)
        assert col == 3

    def test_randomai_name(self) -> None:
        ai = RandomAI()
        assert ai.name == "RandomAI"
