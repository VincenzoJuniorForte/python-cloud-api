#!/usr/bin/env bash

if ! command -v python3 &> /dev/null
then
    echo "Python 3 not found"
    exit
fi

echo "Checking local python virtual environment..."
if [ ! -d ".venv" ]; then
  if cat /etc/os-release | grep -q "ubuntu" || cat /etc/os-release | grep -q "debian"; then
    echo "Installing python venv for debian..."
    sudo apt install python3.10-venv
  fi
  echo "Creating python virtual environment..."
  python3 -m venv .venv
fi

echo "Sourcing python virtual environment..."
source .venv/bin/activate

if ! command -v pip &> /dev/null
then
  echo "pip command not found, reinstalling virtual environment"
  rm -rf .venv
  python3 -m venv .venv
  source .venv/bin/activate
fi


pip-install-quiet() {
  pip install --requirement "$1" --require-virtualenv --quiet
}

echo "Checking/Installing python dependencies..."
pip-install-quiet requirements.txt

