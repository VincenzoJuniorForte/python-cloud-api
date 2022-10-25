#!/usr/bin/env bash
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit

source scripts/init.sh

# firebase init / firebase use ?
# setup the port ?
firebase emulators:start --only firestore &
trap "kill $emulator_pid" EXIT
sleep 3

# TODO not working as expected
export FIRESTORE_EMULATOR_HOST="localhost:8081"
functions-framework --target http_handler --debug