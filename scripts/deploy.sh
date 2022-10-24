#!/usr/bin/env bash
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit

if ! command -v gcloud &> /dev/null
then
    echo "Google Cloud CLI not found. Install instructions -> https://cloud.google.com/sdk/docs/install"
    exit
fi

gcloud functions deploy http-compute-calculation \
  --gen2 \
  --region=europe-west1 \
  --runtime=python310 \
  --entry-point=http_handler \
  --trigger-http \
  --allow-unauthenticated
