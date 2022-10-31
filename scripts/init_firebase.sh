#!/usr/bin/env bash

source scripts/env.sh

if ! command -v firebase &> /dev/null
then
    echo "Firebase CLI not found. Install instructions -> https://firebase.google.com/docs/cli#setup_update_cli"
    exit
fi

# TODO ? Firebase Login
firebase use "$GCLOUD_PROJECT_ID_DEV" > /dev/null