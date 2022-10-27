#!/usr/bin/env bash
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit

source scripts/init_python.sh
source scripts/init_gcloud.sh
source scripts/init_firebase.sh
