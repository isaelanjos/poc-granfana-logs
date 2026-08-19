#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
docker compose up -d --build
printf "\nAPI: http://localhost:8000\nGrafana: http://localhost:3000\nCredenciais: admin/admin\n"
