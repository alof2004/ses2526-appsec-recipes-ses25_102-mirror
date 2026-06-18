# SES 25/26 AppSec Recipes - Group 102

Application security recipes, automation, reports, and evidence for the
ClinicWave clinic management application. This repository complements the
software baseline repository and focuses on threat modelling, SAST, DAST, WAF
validation, and pentesting deliverables.

## Related Repository

The application under test is the ClinicWave software baseline:

- Local sibling directory: `../softwate-baseline-ses25_102`
- Mirror used for workflow validation: <https://github.com/alof2004/ses2526-appsec-recipes-ses25_102-mirror>

The nightly DAST workflow checks out the software repository
`detiuaveiro/softwate-baseline-ses25_102` and scans the configured target ref
(`develop` by default).

## Repository Layout

```text
.
├── .github/workflows/dast-nightly.yml     # Nightly ZAP scans of the software repo
├── dast/
│   ├── scripts/                           # Local DAST helper scripts
│   ├── zap-config/                        # ZAP automation plans
│   └── reports/                           # Stored ZAP reports and WAF logs
├── docs/                                  # Final reports, presentations, diagrams
└── sast/reports/                          # Stored SAST artifacts from project parts 1 and 2
```

## Main Deliverables

- [Final AppSec Report](./docs/FinalReport%20-%20Group%20102%20SES.pdf)
- [Project 1 Presentation](./docs/presentations/Presentation-Project1-SES.pdf)
- [Project 2 Final Presentation](./docs/presentations/FinalPresentation-Project2-SES.pdf)
- [Pentesting Plan](./docs/Pentesting%20Plan.pdf)
- [Pentesting Report](./docs/Pentesting%20Report.pdf)
- DFD diagrams: `docs/dfts/`
- Abuse story and regression images: `docs/images/`

## Security Scope

The AppSec work covers:

- Threat modelling and abuse stories for unauthorized data access, patient
  enumeration, record tampering, cascade deletion, undetectable actions, API
  overload, and related regressions.
- SAST evidence from Gitleaks, Semgrep, ESLint security rules, Trivy dependency
  scans, and Trivy container image scans.
- DAST evidence from OWASP ZAP baseline and active scans.
- WAF validation through Nginx + ModSecurity + OWASP Core Rule Set.
- Pentesting planning and final reporting.

## DAST Automation

The DAST setup uses OWASP ZAP and Docker. The local compose file builds the
backend and frontend from the sibling software repository:

```bash
docker compose -f docker-compose.dast.yml up -d --build db backend frontend
```

### Local Baseline Scan

Run a lightweight ZAP baseline scan against the frontend:

```bash
./dast/scripts/run-dast-baseline.sh
```

Default target inside the Docker network:

```text
http://frontend:5173
```

Override it when needed:

```bash
DAST_BASELINE_TARGET=http://frontend:5173 ./dast/scripts/run-dast-baseline.sh
```

Important: the current production frontend image serves Nginx on container port
`8080`. If the local baseline helper cannot reach the frontend, check
`docker-compose.dast.yml` and either map the frontend service to container port
`8080` or override the scan target to match the running container.

### Local Automation Scan

Run the ZAP automation plan with passive scan, OpenAPI import, spidering,
active scan jobs, and HTML/JSON/SARIF report generation:

```bash
./dast/scripts/run-dast-scan.sh
```

Leave the test stack running after the scan:

```bash
./dast/scripts/run-dast-scan.sh --keep-up
```

Generated local artifacts are written to:

```text
dast/reports/zap-report.html
dast/reports/zap-report.json
dast/reports/zap-report.sarif
dast/reports/zap.out
```

## ZAP Plans

- `dast/zap-config/automation-plan.yaml` scans the application directly:
  frontend routes, backend API routes, OpenAPI docs, spider jobs, passive scan,
  and active scan jobs for patients and appointments.
- `dast/zap-config/automation-plan-waf.yaml` scans the same application surface
  through the WAF endpoint.

Both automation plans inject an `Authorization: Bearer ${ZAP_TOKEN}` header for
API requests when the environment provides `ZAP_TOKEN`.

The automation plans target the Docker-network service names (`frontend`,
`backend`, and `waf`) rather than host ports.

## Nightly DAST Workflow

The AppSec workflow `.github/workflows/dast-nightly.yml` runs daily at 03:00 UTC
and can also be started manually with an optional `target_ref`.

It performs two scans:

- `OWASP ZAP - Direct (no WAF)`: scans the application without the WAF in front.
- `OWASP ZAP - Via WAF (Nginx + ModSecurity CRS)`: scans through the WAF and
  collects `modsec-audit.log` and `nginx-access.log`.

The workflow starts PostgreSQL, Keycloak, backend, frontend, and WAF containers
as needed. It obtains a Keycloak access token for the `admin` test user and
passes that token to ZAP.

The workflow expects a `SOFTWARE_REPO_PAT` secret when checking out the target
software repository.

## Stored Report Artifacts

SAST artifacts are stored under:

```text
sast/reports/part1-reports/
sast/reports/part2-reports/
```

The stored SAST reports include:

- Gitleaks PR SARIF reports.
- Semgrep PR, advisory, and nightly SARIF reports.
- ESLint security JSON reports.
- Trivy filesystem, backend dependency, advisory, backend image, and frontend
  image SARIF reports.

DAST artifacts are stored under:

```text
dast/reports/part1-reports/
dast/reports/part2-reports/
```

The stored DAST reports include:

- ZAP HTML and JSON reports for PR and nightly scans.
- Direct and WAF scan reports for project part 2.
- WAF evidence logs: `modsec-audit.log` and `nginx-access.log`.

## Requirements

- Docker and Docker Compose.
- Bash.
- Python 3 for report summaries in the helper scripts.
  for local DAST runs.

## Useful Commands

Start only the DAST test stack:

```bash
docker compose -f docker-compose.dast.yml up -d --build db backend frontend
```

Stop and remove the DAST stack:

```bash
docker compose -p clinic-dast -f docker-compose.dast.yml down --volumes --remove-orphans
```

Run the baseline scan and keep the app running:

```bash
./dast/scripts/run-dast-baseline.sh --keep-up
```

Run the full local ZAP automation scan:

```bash
./dast/scripts/run-dast-scan.sh
```

## Authors

- Afonso Ferreira, `113480`
- Tomás Brás, `112665`
