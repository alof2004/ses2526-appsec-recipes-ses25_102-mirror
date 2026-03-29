#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if [ -f "${ROOT_DIR}/.env" ]; then
  # shellcheck disable=SC1091
  set -a
  source "${ROOT_DIR}/.env"
  set +a
fi

BACKEND_PORT="${DAST_BACKEND_PORT:-18080}"
FRONTEND_PORT="${DAST_FRONTEND_PORT:-15173}"
TIMEOUT_SECONDS="${1:-180}"
BACKEND_URL="http://localhost:${BACKEND_PORT}/api/patients"
FRONTEND_URL="http://localhost:${FRONTEND_PORT}/patients"
START_TIME="$(date +%s)"

echo "Waiting for backend at ${BACKEND_URL}"
echo "Waiting for frontend at ${FRONTEND_URL}"

while true; do
  if curl -fsS "${BACKEND_URL}" >/dev/null 2>&1 && curl -fsS "${FRONTEND_URL}" >/dev/null 2>&1; then
    echo "Application is reachable."
    exit 0
  fi

  NOW="$(date +%s)"
  if [ $((NOW - START_TIME)) -ge "${TIMEOUT_SECONDS}" ]; then
    echo "Timed out waiting for the application to become ready." >&2
    exit 1
  fi

  sleep 5
done
