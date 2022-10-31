#!/usr/bin/env bash
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit

source scripts/env.sh
source scripts/init_gcloud.sh

run_tests=""
while [[ ! $run_tests == [yYnN] ]]; do
  read -rp "Run the test suite before deploy ? (y/n) " run_tests
done

if [[ $run_tests == [yY] ]]; then
  scripts/run_tests.sh
fi

deploy_production=""
while [[ ! $deploy_production == [yYnN] ]]; do
  read -rp "The function will be deployed to project $GCLOUD_PROJECT_ID_DEV. Deploy to $GCLOUD_PROJECT_ID_PRODUCTION instead ? (y/n) " deploy_production
done

if [[ $deploy_production == [yY] ]]; then
  gcloud config set project "$GCLOUD_PROJECT_ID_PRODUCTION" &>/dev/null
  trap "gcloud config set project $GCLOUD_PROJECT_ID_DEV &>/dev/null" EXIT
fi

if [[ -z $(gcloud services list | grep "Error Reporting") ]]; then
  gcloud services enable clouderrorreporting.googleapis.com
fi

gcloud functions deploy http-compute-calculation \
  --gen2 \
  --region=europe-west1 \
  --runtime=python310 \
  --entry-point=http_handler \
  --trigger-http \
  --allow-unauthenticated
