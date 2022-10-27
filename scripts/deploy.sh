#!/usr/bin/env bash
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit

source scripts/init_gcloud.sh

deploy_production=""
while [[ ! $deploy_production == [yYnN] ]]; do
  read -rp "The function will be deployed to project \"equal-proto-development\". Deploy to \"equal-proto-production\" instead ? (y/N) " deploy_production
done

if [[ $deploy_production == [yY] ]]; then
  gcloud config set project equal-proto-production
  trap "gcloud config set project equal-proto-development" EXIT
else
  gcloud config set project equal-proto-development
fi

if [[ -z $(gcloud services list | grep "Error Reporting") ]]; then
  gcloud services enable clouderrorreporting.googleapis.com
fi

exit
gcloud functions deploy http-compute-calculation \
  --gen2 \
  --region=europe-west1 \
  --runtime=python310 \
  --entry-point=http_handler \
  --trigger-http \
  --allow-unauthenticated
