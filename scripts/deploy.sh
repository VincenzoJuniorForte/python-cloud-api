#!/usr/bin/env bash
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit

source scripts/install_cli_tools.sh

gcloud config set project equal-proto-production
trap "gcloud config set project equal-proto-development" EXIT

gcloud functions deploy http-compute-calculation \
  --gen2 \
  --region=europe-west1 \
  --runtime=python310 \
  --entry-point=http_handler \
  --trigger-http \
  --allow-unauthenticated
