from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def compute_summary(data: dict) -> dict:
    games = data["games"]

    p1_wins = sum(1 for g in games if g["winner"] == 1)
    p2_wins = sum(1 for g in games if g["winner"] == 2)
    draws = sum(1 for g in games if g["winner"] is None)

    p1_durations = [
        m["duration"]
        for g in games
        for m in g["moves"]
        if m["player"] == 1 and m["duration"] is not None
    ]
    p2_durations = [
        m["duration"]
        for g in games
        for m in g["moves"]
        if m["player"] == 2 and m["duration"] is not None
    ]

    p1_avg_duration = sum(p1_durations) / len(p1_durations) if p1_durations else None
    p2_avg_duration = sum(p2_durations) / len(p2_durations) if p2_durations else None

    res_games = [g for g in games if g.get("resources") is not None]

    if res_games:
        p1_wall = [g["resources"]["player1"]["wall_time"] for g in res_games]
        p2_wall = [g["resources"]["player2"]["wall_time"] for g in res_games]
        p1_ram = [g["resources"]["player1"]["peak_ram_bytes"] for g in res_games]
        p2_ram = [g["resources"]["player2"]["peak_ram_bytes"] for g in res_games]

        p1_ai_data = {
            "average_turn_duration": p1_avg_duration,
            "average_wall_time": sum(p1_wall) / len(p1_wall),
            "average_peak_ram_bytes": sum(p1_ram) / len(p1_ram),
            "maximum_peak_ram_bytes": max(p1_ram),
            "minimum_peak_ram_bytes": min(p1_ram),
        }
        p2_ai_data = {
            "average_turn_duration": p2_avg_duration,
            "average_wall_time": sum(p2_wall) / len(p2_wall),
            "average_peak_ram_bytes": sum(p2_ram) / len(p2_ram),
            "maximum_peak_ram_bytes": max(p2_ram),
            "minimum_peak_ram_bytes": min(p2_ram),
        }
    else:
        p1_ai_data = {
            "average_turn_duration": p1_avg_duration,
            "average_wall_time": None,
            "average_peak_ram_bytes": None,
            "maximum_peak_ram_bytes": None,
            "minimum_peak_ram_bytes": None,
        }
        p2_ai_data = {
            "average_turn_duration": p2_avg_duration,
            "average_wall_time": None,
            "average_peak_ram_bytes": None,
            "maximum_peak_ram_bytes": None,
            "minimum_peak_ram_bytes": None,
        }

    return {
        "games": len(games),
        "mode": games[0]["mode"] if games else "",
        "p1_ai_name": data.get("p1_name", ""),
        "p2_ai_name": data.get("p2_name", ""),
        "p1_ai_wins": p1_wins,
        "p2_ai_wins": p2_wins,
        "draws": draws,
        "p1_ai_data": p1_ai_data,
        "p2_ai_data": p2_ai_data,
    }


def load_results(path: Path) -> dict:
    path = Path(path)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(1)
    if "games" not in data:
        print(f"Error: missing 'games' key in {path}", file=sys.stderr)
        sys.exit(1)
    return data


def write_summary(summary: dict, input_path: Path) -> Path:
    input_path = Path(input_path)
    output_path = input_path.parent / f"{input_path.stem}_summary.json"
    output_path.write_text(json.dumps(summary, indent=2))
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize Connect Four results")
    parser.add_argument("results_file", type=Path, help="Path to results JSON file")
    args = parser.parse_args()

    data = load_results(args.results_file)
    summary = compute_summary(data)
    output_path = write_summary(summary, args.results_file)
    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()
