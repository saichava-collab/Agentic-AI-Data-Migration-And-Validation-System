#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH="$(pwd)"

python scripts/setup_demo.py
python jobs/batch_migration.py
python validators/run_validation.py
python scripts/generate_expected_outputs.py

echo "All batch steps completed successfully"
