"""Tests for CLI helper functions (_parse_ai_params and _load_ai_class)."""

from __future__ import annotations

import pytest

from connect_four.ai.mcts_ai import MctsAI
from connect_four.cli import _parse_ai_params, _load_ai_class


# ---------------------------------------------------------------------------
# 1. _parse_ai_params
# ---------------------------------------------------------------------------


class TestParseAiParams:
    def test_none_returns_empty_dict(self) -> None:
        assert _parse_ai_params(None) == {}

    def test_empty_list_returns_empty_dict(self) -> None:
        assert _parse_ai_params([]) == {}

    def test_single_int_param(self) -> None:
        assert _parse_ai_params(["iterations=500"]) == {"iterations": 500}

    def test_single_float_param(self) -> None:
        assert _parse_ai_params(["exploration=1.41"]) == {"exploration": 1.41}

    def test_bool_true(self) -> None:
        assert _parse_ai_params(["verbose=true"]) == {"verbose": True}

    def test_bool_false(self) -> None:
        assert _parse_ai_params(["debug=False"]) == {"debug": False}

    def test_string_fallback(self) -> None:
        assert _parse_ai_params(["name=my_ai"]) == {"name": "my_ai"}

    def test_multiple_params(self) -> None:
        result = _parse_ai_params(["depth=3", "exploration=1.41"])
        assert result == {"depth": 3, "exploration": 1.41}

    def test_negative_int(self) -> None:
        assert _parse_ai_params(["penalty=-5"]) == {"penalty": -5}

    def test_missing_equals_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid parameter format"):
            _parse_ai_params(["iterations"])

    def test_value_with_equals_sign(self) -> None:
        assert _parse_ai_params(["formula=a=b"]) == {"formula": "a=b"}


# ---------------------------------------------------------------------------
# 2. _load_ai_class
# ---------------------------------------------------------------------------


class TestLoadAiClassWithParams:
    def test_load_without_params(self) -> None:
        instance = _load_ai_class("connect_four.ai.random_ai.RandomAI")
        assert instance is not None

    def test_load_with_params(self) -> None:
        instance = _load_ai_class("connect_four.ai.mcts_ai.MctsAI", {"iterations": 500})
        assert isinstance(instance, MctsAI)
        assert instance._iterations == 500

    def test_load_with_empty_params(self) -> None:
        instance = _load_ai_class("connect_four.ai.mcts_ai.MctsAI", {})
        assert isinstance(instance, MctsAI)
        assert instance._iterations == 1000

    def test_load_with_unknown_param_exits(self) -> None:
        with pytest.raises(SystemExit):
            _load_ai_class("connect_four.ai.mcts_ai.MctsAI", {"unknown_param": 42})
