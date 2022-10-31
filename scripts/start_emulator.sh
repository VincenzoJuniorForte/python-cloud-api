#!/usr/bin/env bash

if ! command -v java &> /dev/null
then
    echo "Java OpenJDK not found. Install instructions https://openjdk.org/install/"
    exit
fi

if ! command -v node &> /dev/null
then
    echo "Node not found. Install instructions https://nodejs.org/en/download/package-manager/"
    exit
fi

echo "Starting emulators..."
firebase emulators:start --only firestore &
export FIRESTORE_EMULATOR_HOST="localhost:8081"
trap "pkill firebase" EXIT
sleep 3
