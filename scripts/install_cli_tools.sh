#!/usr/bin/env bash

if ! command -v gcloud &> /dev/null
then
    echo "Google Cloud CLI not found. Install instructions -> https://cloud.google.com/sdk/docs/install"
    exit
fi

if ! command -v firebase &> /dev/null
then
    echo "Firebase CLI not found. Install instructions -> https://firebase.google.com/docs/cli#setup_update_cli"
    exit
fi
