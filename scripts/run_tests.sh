#!/usr/bin/env bash
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit

source scripts/init.sh

echo "Checking/Installing python test dependencies..."
pip-install-quiet test_requirements.txt

source scripts/start_emulator.sh

echo "Starting Pytest..."
pytest