#!/usr/bin/env bash

if ! command -v python3 &> /dev/null
then
    echo "Python 3 not found"
    exit
fi

if [ ! -d ".venv" ]; then
  python -m venv .venv
fi
source .venv/bin/activate

pip-install-quiet() {
  pip install --requirement "$1" --require-virtualenv --quiet
}

pip-install-quiet requirements.txt

