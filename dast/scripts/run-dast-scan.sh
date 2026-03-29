#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
COMPOSE_FILE="${ROOT_DIR}/docker-compose.dast.yml"
PROJECT_NAME="${COMPOSE_PROJECT_NAME:-clinic-dast}"
REPORTS_DIR="${ROOT_DIR}/dast/reports"
KEEP_STACK=0

if [ "${1:-}" = "--keep-up" ]; then
  KEEP_STACK=1
fi

cleanup() {
  if [ "${KEEP_STACK}" -eq 0 ]; then
    docker compose -p "${PROJECT_NAME}" -f "${COMPOSE_FILE}" down --volumes --remove-orphans
  fi
}

trap cleanup EXIT

echo "Starting local DAST scan for Clinic Management Application"
mkdir -p "${REPORTS_DIR}"
rm -f "${REPORTS_DIR}/zap-report.html" "${REPORTS_DIR}/zap-report.json" "${REPORTS_DIR}/zap-report.sarif" "${REPORTS_DIR}/zap-report.sarif.json"
# ZAP writes reports from inside a container as the non-root `zap` user. On CI
# bind mounts, the host directory ownership often does not match that UID, so
# make the report directory world-writable before starting the scanner.
chmod 0777 "${REPORTS_DIR}"

docker compose -p "${PROJECT_NAME}" -f "${COMPOSE_FILE}" up -d --build db backend frontend
"${ROOT_DIR}/dast/scripts/wait-for-app.sh" 240

echo "Running OWASP ZAP automation plan"
set +e
docker compose --profile scanner -p "${PROJECT_NAME}" -f "${COMPOSE_FILE}" run --rm zap
ZAP_EXIT_CODE=$?
set -e

if [ -f "${REPORTS_DIR}/zap-report.sarif.json" ] && [ ! -f "${REPORTS_DIR}/zap-report.sarif" ]; then
  mv "${REPORTS_DIR}/zap-report.sarif.json" "${REPORTS_DIR}/zap-report.sarif"
fi

echo
echo "DAST report summary"
if [ -f "${REPORTS_DIR}/zap-report.json" ]; then
  python3 - <<'PY'
import json
from pathlib import Path

report = json.loads(Path("dast/reports/zap-report.json").read_text())
counts = {"High": 0, "Medium": 0, "Low": 0, "Informational": 0}
seen_alerts = set()
for site in report.get("site", []):
    for alert in site.get("alerts", []):
        riskdesc = alert.get("riskdesc") or alert.get("risk") or ""
        severity = riskdesc.split(" ", 1)[0] if riskdesc else "Informational"
        if severity == "Info":
            severity = "Informational"

        key = (alert.get("pluginid"), alert.get("name"), severity)
        if key in seen_alerts:
            continue

        seen_alerts.add(key)
        counts[severity] = counts.get(severity, 0) + 1

for level in ("High", "Medium", "Low", "Informational"):
    print(f"{level}: {counts.get(level, 0)}")
print(f"Total: {sum(counts.values())}")
PY
else
  echo "No JSON report was generated."
fi

echo
echo "Artifacts:"
echo "  ${REPORTS_DIR}/zap-report.html"
echo "  ${REPORTS_DIR}/zap-report.json"
echo "  ${REPORTS_DIR}/zap-report.sarif"

if [ "${KEEP_STACK}" -eq 1 ]; then
  trap - EXIT
  echo
  echo "Application stack left running under compose project ${PROJECT_NAME}."
fi

exit "${ZAP_EXIT_CODE}"
