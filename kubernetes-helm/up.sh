#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
helm upgrade --install observability "$SCRIPT_DIR" \
  --namespace observability \
  --create-namespace \
  --wait
printf "\nAmbiente Helm instalado.\n"
printf "Valide com: kubectl -n observability get pods\n"
