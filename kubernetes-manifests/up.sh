#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
for manifest in \
  "$SCRIPT_DIR/00-namespace.yaml" \
  "$SCRIPT_DIR/01-api.yaml" \
  "$SCRIPT_DIR/02-loki.yaml" \
  "$SCRIPT_DIR/03-grafana.yaml" \
  "$SCRIPT_DIR/04-alloy.yaml" \
  "$SCRIPT_DIR/05-gateway.yaml"; do
  kubectl apply -f "$manifest"
done
printf "\nAmbiente Kubernetes puro aplicado.\n"
printf "Valide com: kubectl -n observability get pods\n"
