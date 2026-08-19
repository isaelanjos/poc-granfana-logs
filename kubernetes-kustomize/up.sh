#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
kubectl apply -k "$SCRIPT_DIR/overlays/local"
printf "\nAmbiente Kustomize aplicado.\n"
printf "Valide com: kubectl -n observability get pods\n"
