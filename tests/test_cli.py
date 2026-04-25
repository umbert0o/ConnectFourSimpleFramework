"""Tests for CLI helper functions (_parse_ai_params and _load_ai_class)."""

from __future__ import annotations

import pytest

from connect_four.ai.mcts_ai import MCTSAI
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
        instance = _load_ai_class("connect_four.ai.mcts_ai.MCTSAI", {"iterations": 500})
        assert isinstance(instance, MCTSAI)
        assert instance._iterations == 500

    def test_load_with_empty_params(self) -> None:
        instance = _load_ai_class("connect_four.ai.mcts_ai.MCTSAI", {})
        assert isinstance(instance, MCTSAI)
        assert instance._iterations == 1000

    def test_load_with_unknown_param_exits(self) -> None:
        with pytest.raises(SystemExit):
            _load_ai_class("connect_four.ai.mcts_ai.MCTSAI", {"unknown_param": 42})


# ---------------------------------------------------------------------------
# 3. --workers / -j flag
# ---------------------------------------------------------------------------


class TestWorkersFlag:
    def test_workers_flag_exists(self) -> None:
        from connect_four.cli import _build_parser

        parser = _build_parser()
        args = parser.parse_args(
            [
                "--headless",
                "--p1-ai",
                "connect_four.ai.random_ai.RandomAI",
                "--p2-ai",
                "connect_four.ai.random_ai.RandomAI",
                "-j",
                "4",
            ]
        )
        assert args.workers == 4

    def test_workers_long_form(self) -> None:
        from connect_four.cli import _build_parser

        parser = _build_parser()
        args = parser.parse_args(
            [
                "--headless",
                "--p1-ai",
                "connect_four.ai.random_ai.RandomAI",
                "--p2-ai",
                "connect_four.ai.random_ai.RandomAI",
                "--workers",
                "8",
            ]
        )
        assert args.workers == 8

    def test_workers_default_is_none(self) -> None:
        from connect_four.cli import _build_parser

        parser = _build_parser()
        args = parser.parse_args(
            [
                "--headless",
                "--p1-ai",
                "connect_four.ai.random_ai.RandomAI",
                "--p2-ai",
                "connect_four.ai.random_ai.RandomAI",
            ]
        )
        assert args.workers is None

    def test_workers_passed_to_run_headless(self) -> None:
        from unittest.mock import patch
        from connect_four.cli import main

        with patch("connect_four.headless_runner.run_headless") as mock_run:
            mock_run.return_value = {"player1_wins": 0, "player2_wins": 0, "draws": 0}
            with patch(
                "sys.argv",
                [
                    "connect_four",
                    "--headless",
                    "--p1-ai",
                    "connect_four.ai.random_ai.RandomAI",
                    "--p2-ai",
                    "connect_four.ai.random_ai.RandomAI",
                    "-j",
                    "4",
                ],
            ):
                main()
            mock_run.assert_called_once()
            call_kwargs = mock_run.call_args.kwargs
            assert "workers" in call_kwargs
            assert call_kwargs["workers"] == 4
            assert call_kwargs["workers"] == 4
