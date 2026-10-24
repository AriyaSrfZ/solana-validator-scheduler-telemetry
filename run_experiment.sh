#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Running Invariant and Telemetry Unit Tests ==="
python3 -m unittest discover -s tests -p "test_*.py" -v

echo -e "\n=== Running Validator Scheduler Telemetry (Dry-Run Mode) ==="
python3 -m src.telemetry_collector --data-dir ./data

echo -e "\nTelemetry execution successfully verified."
