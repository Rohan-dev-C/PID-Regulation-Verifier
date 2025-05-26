#!/bin/bash

# Fail fast if any command fails
set -e

echo "Running PID Regulation Verifier pipeline..."

# Paths
PID="data/pid/diagram.pdf"
SOP="data/sop/sop.docx"
OUT="output"

# Run CLI pipeline
python -m src.main --pid "$PID" --sop "$SOP" --out "$OUT"

echo "✅ Pipeline complete."
echo "  - Graph:        $OUT/graphs/pid_graph.gpickle"
echo "  - Discrepancies: $OUT/logs/discrepancies.jsonl"
