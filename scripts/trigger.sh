#!/usr/bin/env bash
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit

source scripts/init_gcloud.sh

remote=""
while [[ ! $remote == [rRlL] ]]; do
  read -rp "Trigger on localhost (l) or on the remote cloud server (r) ? (r/l) " remote
done

if [[ $remote == [rR] ]]; then
  URL=$(gcloud functions describe http-compute-calculation --gen2 --region europe-west1 --format="value(serviceConfig.uri)")
else
  URL="localhost:8080"
fi

PAYLOAD="$*"

if [[ -z $PAYLOAD ]]; then
  PAYLOAD='{"operation": "x = 1", "step": "x = 1", "user_id": "user-1", "exercise_id": "exercise-1"}'
fi

curl -v "$URL" \
-H 'Content-Type: application/json' \
-d "$PAYLOAD"

