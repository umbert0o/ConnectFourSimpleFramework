from __future__ import annotations

import argparse
import importlib
import sys

from connect_four.ai.ai_base import AIBase
from connect_four.game.game import Game


def _parse_ai_params(params: list[str] | None) -> dict[str, int | float | bool | str]:
    if not params:
        return {}
    result: dict[str, int | float | bool | str] = {}
    for item in params:
        if "=" not in item:
            raise ValueError(
                f"Invalid parameter format '{item}'. Expected 'key=value'."
            )
        key, value = item.split("=", 1)
        if value.lstrip("-").isdigit():
            result[key] = int(value)
        else:
            try:
                result[key] = float(value)
            except ValueError:
                if value.lower() == "true":
                    result[key] = True
                elif value.lower() == "false":
                    result[key] = False
                else:
                    result[key] = value
    return result


def _load_ai_class(dotted_path: str, params: dict | None = None) -> AIBase:
    if "." not in dotted_path:
        print(
            f"Error: Invalid AI path '{dotted_path}'. Expected 'module.ClassName' format."
        )
        sys.exit(1)

    module_path, class_name = dotted_path.rsplit(".", 1)

    try:
        module = importlib.import_module(module_path)
    except ImportError as exc:
        print(f"Error: Could not load AI class '{dotted_path}': {exc}")
        sys.exit(1)

    try:
        cls = getattr(module, class_name)
    except AttributeError:
        print(
            f"Error: Could not load AI class '{dotted_path}': module '{module_path}' has no attribute '{class_name}'"
        )
        sys.exit(1)

    if not (isinstance(cls, type) and issubclass(cls, AIBase)):
        print(f"Error: '{dotted_path}' is not a valid AI class")
        sys.exit(1)

    try:
        return cls(**(params or {}))
    except Exception as exc:
        print(f"Error: Could not instantiate AI class '{dotted_path}': {exc}")
        sys.exit(1)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="connect_four",
        description="Connect Four Framework — play or pit AIs against each other.",
    )
    parser.add_argument(
        "--p1-ai",
        default=None,
        help="Dotted path to AI class for Player 1. If omitted, P1 is human-controlled.",
    )
    parser.add_argument(
        "--p2-ai",
        default=None,
        help="Dotted path to AI class for Player 2. If omitted, P2 is human-controlled.",
    )
    parser.add_argument(
        "--p1-ai-params",
        nargs="*",
        default=None,
        metavar="KEY=VALUE",
        help="Parameters to pass to P1 AI constructor (e.g. iterations=100).",
    )
    parser.add_argument(
        "--p2-ai-params",
        nargs="*",
        default=None,
        metavar="KEY=VALUE",
        help="Parameters to pass to P2 AI constructor (e.g. iterations=100).",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run without visual display (requires both --p1-ai and --p2-ai).",
    )
    parser.add_argument(
        "--games",
        type=int,
        default=1,
        help="Number of games for headless mode (default: 1).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=None,
        help="Timeout in seconds for each AI move (UNIX only).",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Export headless results to a JSON file.",
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    p1_params = _parse_ai_params(args.p1_ai_params)
    p2_params = _parse_ai_params(args.p2_ai_params)
    p1_ai = _load_ai_class(args.p1_ai, p1_params) if args.p1_ai else None
    p2_ai = _load_ai_class(args.p2_ai, p2_params) if args.p2_ai else None

    if args.headless:
        if p1_ai is None or p2_ai is None:
            parser.error("--headless requires both --p1-ai and --p2-ai.")
        from connect_four.headless_runner import run_headless

        run_headless(p1_ai, p2_ai, games=args.games, output_path=args.output)
        return

    game = Game()
    from connect_four.ui.game_controller import VisualGameController
    from connect_four.ui.renderer import PygameRenderer

    renderer = PygameRenderer(game)
    controller = VisualGameController(
        game, renderer, p1_ai=p1_ai, p2_ai=p2_ai, timeout_seconds=args.timeout
    )
    controller.run()
