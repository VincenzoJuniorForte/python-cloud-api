#!/usr/bin/env bash
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit

source scripts/init.sh
source scripts/start_emulator.sh

functions-framework --target http_handler --debug
