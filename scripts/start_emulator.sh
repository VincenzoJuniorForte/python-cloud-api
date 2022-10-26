#!/usr/bin/env bash

firebase emulators:start --only firestore &
export FIRESTORE_EMULATOR_HOST="localhost:8081"
trap "pkill firebase" EXIT
sleep 3
