#!/usr/bin/env bash

source scripts/env.sh

if ! command -v firebase &> /dev/null
then
    echo "Firebase CLI not found. Install instructions -> https://firebase.google.com/docs/cli#setup_update_cli"
    echo "Trying auto install..."
    curl -sL https://firebase.tools | bash
    exit
fi

echo "Setting project to development..."
firebase use "$GCLOUD_PROJECT_ID_DEV" > /dev/null