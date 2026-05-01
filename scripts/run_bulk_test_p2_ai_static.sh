#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────────────────────
# Path Resolution (Handles execution from scripts/)
# ─────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." &>/dev/null && pwd)"

# Change to project root so `python -m connect_four` resolves the package [[citation:3]]
cd "$PROJECT_ROOT"
export PYTHONPATH="$PROJECT_ROOT:${PYTHONPATH:-}"

# ─────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────
P1_AI="connect_four.ai.mcts_ai.MCTSAI"
P2_AI="connect_four.ai.mcts_ai.MCTSAI"

# P2 is now static with the baseline parameters
P2_PARAMS=("iterations=1000" "exploration_weight=1")

WORKERS=10
GAMES=1000
# Relative to project root for consistent artifact storage
OUTPUT_DIR="results_"
RESULTS_FILES=()

mkdir -p "$OUTPUT_DIR"

echo "🚀 Starting headless tournament runs from: $PROJECT_ROOT"

# Loop 0 to 20 → 0.0 to 2.0 in 0.1 increments (21 iterations)
for i in $(seq 0 20); do
    EXPL_WEIGHT=$(awk "BEGIN {printf \"%.1f\", $i/10}")
    
    # P1 is now dynamic
    P1_PARAMS=("iterations=1000" "exploration_weight=${EXPL_WEIGHT}")
    
    # Updated filename to reflect P1 dynamic / P2 static
    OUTPUT_FILE="${OUTPUT_DIR}/MCTS1_1000-${EXPL_WEIGHT}_vs_MCTS2_1000-1.json"

    echo "[$((i+1))/21] P1 exploration_weight=${EXPL_WEIGHT} → ${OUTPUT_FILE}"

    python -m connect_four \
        --headless \
        --p1-ai "$P1_AI" \
        --p1-ai-params "${P1_PARAMS[@]}" \
        --p2-ai "$P2_AI" \
        --p2-ai-params "${P2_PARAMS[@]}" \
        -j "$WORKERS" \
        --games "$GAMES" \
        --output "$OUTPUT_FILE"

    RESULTS_FILES+=("$OUTPUT_FILE")
done

echo "✅ All headless runs completed."
echo "📊 Triggering summarize_results.py on each output file..."

for file in "${RESULTS_FILES[@]}"; do
    echo "Summarizing: ${file}"
    # Invokes the CLI summarizer tool [[citation:1]]
    python -m connect_four.summarize_results "$file"
done

echo "🎉 All summaries generated. Check ${OUTPUT_DIR}/ for results."