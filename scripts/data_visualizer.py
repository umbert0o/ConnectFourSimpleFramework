#!/usr/bin/env python3
"""
Modular script to visualize AI comparison results from _summary.json files.
Designed to run from scripts/ or project root.
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd
import matplotlib.pyplot as plt

# ─────────────────────────────────────────────────────────────
# 1. Data Extraction Module
# ─────────────────────────────────────────────────────────────
class SummaryExtractor:
    def __init__(self, directory: Path, param_regex: str = r'MCTS1_\d+-(\d+(?:\.\d+)?)_vs_'):
        self.dir_path = Path(directory)
        self.param_re = re.compile(param_regex)

    def _get_nested(self, data: Dict, key_path: str, default=None) -> Any:
        """Safely traverse nested dictionaries (e.g., 'p1_ai_data.average_turn_duration')."""
        keys = key_path.split(".")
        val = data
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                return default
        return val

    def load_directory(self) -> pd.DataFrame:
        records = []
        summary_files = sorted(self.dir_path.glob("*_summary.json"))
        
        if not summary_files:
            print(f"Warning: No _summary.json files found in {self.dir_path}")
            return pd.DataFrame()

        for fp in summary_files:
            try:
                with open(fp) as f:
                    data = json.load(f)
                
                # Extract the varying parameter from the filename [[citation:3]][[citation:4]]
                match = self.param_re.search(fp.name)
                param = float(match.group(1)) if match else 0.0
                
                games = self._get_nested(data, "games", 0) or 1 # Avoid div by zero
                
                records.append({
                    "parameter": param,
                    "p1_wins": self._get_nested(data, "p1_ai_wins", 0),
                    "p2_wins": self._get_nested(data, "p2_ai_wins", 0),
                    "draws": self._get_nested(data, "draws", 0),
                    "p1_win_rate": self._get_nested(data, "p1_ai_wins", 0) / games,
                    "p1_avg_turn": self._get_nested(data, "p1_ai_data.average_turn_duration"),
                    "p2_avg_turn": self._get_nested(data, "p2_ai_data.average_turn_duration"),
                    "p1_avg_ram": self._get_nested(data, "p1_ai_data.average_peak_ram_bytes"),
                    "p2_avg_ram": self._get_nested(data, "p2_ai_data.average_peak_ram_bytes"),
                })
            except Exception as e:
                print(f"Error processing {fp}: {e}")

        return pd.DataFrame(records)

# ─────────────────────────────────────────────────────────────
# 2. Diagram Generation Module
# ─────────────────────────────────────────────────────────────
class DiagramGenerator:
    def __init__(self, output_dir: Path):
        self.out_dir = Path(output_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        plt.style.use("seaborn-v0_8-whitegrid")

    def batch_plot(self, df: pd.DataFrame, configs: List[Dict]) -> None:
        if df.empty:
            return

        for cfg in configs:
            fig, ax = plt.subplots(figsize=(10, 6))
            x, y_cols = cfg["x"], cfg["y"]
            ptype = cfg.get("type", "line")
            colors = plt.cm.Set2.colors[:len(y_cols)]
            
            if ptype == "line":
                for i, col in enumerate(y_cols):
                    ax.plot(df[x], df[col], marker="o", label=col, color=colors[i])
            elif ptype == "bar":
                width = 0.3 / len(y_cols)
                for i, col in enumerate(y_cols):
                    ax.bar(df[x] + (i - len(y_cols)/2 + 0.5)*width, df[col], width, label=col, color=colors[i])
            elif ptype == "scatter":
                for i, col in enumerate(y_cols):
                    ax.scatter(df[x], df[col], label=col, color=colors[i])
                    
            ax.set_xlabel(x.replace("_", " ").title())
            ax.set_ylabel("Value")
            ax.set_title(cfg["title"])
            ax.legend()
            fig.tight_layout()
            
            save_path = self.out_dir / f"{cfg['filename']}.png"
            fig.savefig(save_path, dpi=150)
            plt.close(fig)
            print(f"✓ Saved: {save_path}")

# ─────────────────────────────────────────────────────────────
# 3. Main Execution & Path Resolution
# ─────────────────────────────────────────────────────────────
def run_analysis(directories: List[Path], output_base: Path) -> None:
    # Configuration for which metrics to visualize [[citation:1]]
    plot_configs = [
        {"title": "Win Rate vs Parameter", "x": "parameter", "y": ["p1_win_rate"], "type": "line", "filename": "win_rate"},
        {"title": "Average Turn Duration", "x": "parameter", "y": ["p1_avg_turn", "p2_avg_turn"], "type": "line", "filename": "turn_duration"},
        {"title": "Peak RAM Usage", "x": "parameter", "y": ["p1_avg_ram", "p2_avg_ram"], "type": "bar", "filename": "ram_usage"},
        {"title": "Turn Duration Scatter", "x": "parameter", "y": ["p1_avg_turn", "p2_avg_turn"], "type": "scatter", "filename": "turn_scatter"},
    ]

    for dir_name in directories:
        if not dir_name.exists():
            print(f"Skipping missing directory: {dir_name}")
            continue
            
        print(f"\n📊 Processing directory: {dir_name}")
        extractor = SummaryExtractor(directory=dir_name)
        df = extractor.load_directory()
        
        # Create output folder specific to the input context
        out_dir = output_base / dir_name.name
        generator = DiagramGenerator(output_dir=out_dir)
        generator.batch_plot(df, plot_configs)
        print(f"✅ Completed: {out_dir}")

if __name__ == "__main__":
    # Path Resolution Logic matching bash scripts [[citation:3]][[citation:4]]
    SCRIPT_DIR = Path(__file__).resolve().parent
    
    # If script is in 'scripts/', move up to project root. Otherwise assume current dir is root.
    PROJECT_ROOT = SCRIPT_DIR.parent if SCRIPT_DIR.name == "scripts" else SCRIPT_DIR
    
    # Ensure imports work if running from outside the virtualenv or repo root
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    # Target directories defined relative to the resolved project root
    TARGET_DIRS = [
        PROJECT_ROOT / "results_" / "p1_ai_static",
        PROJECT_ROOT / "results_" / "p2_ai_static",
    ]
    
    run_analysis(TARGET_DIRS, output_base=PROJECT_ROOT / "ai_comparison_diagrams")