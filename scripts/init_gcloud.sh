#!/usr/bin/env bash

source scripts/env.sh

if ! command -v gcloud &> /dev/null
then
    echo "Google Cloud CLI not found. Install instructions -> https://cloud.google.com/sdk/docs/install"
    exit
fi

if [[ -z $(gcloud config list account --format "value(core.account)") ]]; then
  echo "Logging into google cloud..."
  gcloud auth login
fi
if [ ! -f "$HOME/.config/gcloud/application_default_credentials.json" ]; then
  echo "Setting default credentials for scripts..."
  gcloud auth application-default login
fi

echo "Setting project to development..."
gcloud config set project "$GCLOUD_PROJECT_ID_DEV" &> /dev/null
