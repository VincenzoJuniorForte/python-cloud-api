#!/usr/bin/env bash

if ! command -v firebase &> /dev/null
then
    echo "Firebase CLI not found. Install instructions -> https://firebase.google.com/docs/cli#setup_update_cli"
    exit
fi

# TODO ? Firebase Login
firebase use equal-proto-development > /dev/null