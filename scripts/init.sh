#!/usr/bin/env bash
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit

if [ ! -d ".venv" ]; then
  python -m venv .venv
fi
source .venv/bin/activate

pip-install-quiet() {
  pip install --requirement "$1" --require-virtualenv --quiet
}

pip-install-quiet requirements.txt

source scripts/install_cli_tools.sh

gcloud config set project equal-proto-development > /dev/null
firebase use equal-proto-development > /dev/null