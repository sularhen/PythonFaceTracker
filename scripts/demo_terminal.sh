#!/usr/bin/env bash
set -euo pipefail

INPUT_PATH="${1:-./media}"
OUTPUT_PATH="${2:-./output}"

echo "1. Creating virtual environment"
python -m venv .venv

echo "2. Activating virtual environment"
source .venv/bin/activate

echo "3. Installing FaceTrail in editable mode"
python -m pip install -e .

echo "4. Running terminal scan"
facetrail scan "$INPUT_PATH" --output "$OUTPUT_PATH" --engine auto --save-redacted --open-report

echo "5. Launching desktop GUI"
facetrail gui
