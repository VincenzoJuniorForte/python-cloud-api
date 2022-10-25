#!/usr/bin/env bash
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit

source scripts/init.sh

pip-install-quiet test_requirements.txt

pytest

