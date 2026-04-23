from __future__ import annotations

import argparse
import importlib
import sys

from connect_four.ai.ai_base import AIBase
from connect_four.game.game import Game


def _load_ai_class(dotted_path: str) -> AIBase:
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
        return cls()
    except Exception as exc:
        print(f"Error: Could not instantiate AI class '{dotted_path}': {exc}")
        sys.exit(1)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="connect_four",
        description="Connect Four Framework — play or pit AIs against each other.",
    )
    parser.add_argument(
        "--mode",
        required=True,
        choices=["human-vs-ai", "ai-vs-ai"],
        help="Game mode to run.",
    )
    parser.add_argument(
        "--ai",
        default="connect_four.ai.random_ai.RandomAI",
        help="Dotted path to AI class for human-vs-ai mode (default: connect_four.ai.random_ai.RandomAI).",
    )
    parser.add_argument(
        "--ai1",
        default="connect_four.ai.random_ai.RandomAI",
        help="Dotted path to Player 1 AI class for ai-vs-ai mode (default: connect_four.ai.random_ai.RandomAI).",
    )
    parser.add_argument(
        "--ai2",
        default="connect_four.ai.random_ai.RandomAI",
        help="Dotted path to Player 2 AI class for ai-vs-ai mode (default: connect_four.ai.random_ai.RandomAI).",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run without visual display (ai-vs-ai mode only).",
    )
    parser.add_argument(
        "--games",
        type=int,
        default=1,
        help="Number of games for headless ai-vs-ai (default: 1).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=None,
        help="Timeout in seconds for each AI move (UNIX only).",
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.mode == "human-vs-ai":
        ai = _load_ai_class(args.ai)
        game = Game()
        # ai_player plays as PLAYER_2, human is always PLAYER_1
        from connect_four.ui.game_controller import VisualGameController
        from connect_four.ui.renderer import PygameRenderer

        renderer = PygameRenderer(game)
        controller = VisualGameController(
            game, renderer, ai=ai, timeout_seconds=args.timeout
        )
        controller.run()

    elif args.mode == "ai-vs-ai":
        ai1 = _load_ai_class(args.ai1)
        ai2 = _load_ai_class(args.ai2)

        if args.headless:
            from connect_four.headless_runner import run_headless

            run_headless(ai1, ai2, games=args.games)
        else:
            game = Game()
            from connect_four.ui.game_controller import VisualGameController
            from connect_four.ui.renderer import PygameRenderer

            renderer = PygameRenderer(game)
            controller = VisualGameController(
                game, renderer, ai1=ai1, ai2=ai2, timeout_seconds=args.timeout
            )
            controller.run()
