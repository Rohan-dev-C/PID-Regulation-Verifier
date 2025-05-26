#!/bin/bash

set -e

echo "Running PID Regulation Verifier pipeline..."

PID="data/pid/diagram.pdf"
SOP="data/sop/sop.docx"
OUT="output"

python -m src.main --pid "$PID" --sop "$SOP" --out "$OUT"

echo "✅ Pipeline complete."
echo "  - Graph:        $OUT/graphs/pid_graph.gpickle"
echo "  - Discrepancies: $OUT/logs/discrepancies.jsonl"
