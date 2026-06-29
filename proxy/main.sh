#!/usr/bin/env bash

set -euo pipefail

arguments=(
  --mode=wireguard
  --set=showhost=true
)

for script in "${HOME}"/addons/*.py
do
  arguments+=(--scripts="${script}")
done

exec mitmdump "${arguments[@]}"
