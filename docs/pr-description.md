# Part 2 — Perimeter WAF, JWT+RBAC regression update, and frontend hardening

## Summary

- **Nginx + ModSecurity CRS WAF** added as the sole public entry point to the API. All traffic goes through TLS termination, OWASP CRS 4.25.0 in blocking mode (paranoia level 1), IP rate limiting (30 req/s burst 60), and request-size limits. Backend port is no longer exposed on the host.
- **mkcert TLS** replaces the self-signed cert generated at build time — the browser trusts the certificate without warnings. The WAF container runs as non-root (`USER nginx`).
- **Frontend converted to static build** — multi-stage Dockerfile compiles with Node and serves the bundle with Nginx (non-root). The Vite dev server no longer runs in the container. `VITE_API_BASE_URL` is baked in at build time pointing directly to the WAF. Security headers (`X-Frame-Options`, `X-Content-Type-Options`, `CSP`, `Permissions-Policy`, `CORP`, `Referrer-Policy`) added to frontend Nginx; `server_tokens off` to suppress version disclosure.
- **PUT/DELETE unblocked** — CRS rule 911100 method enforcement extended to include PUT and DELETE via the `ALLOWED_METHODS` env var, which the base image entrypoint passes to `tx.allowed_methods`.
- **Two-run DAST workflow** — `zap-direct` (no WAF, baseline) and `zap-via-waf` (through ModSecurity) jobs run on every PR; ModSec audit log collected as artifact for before/after evidence. Audit log collection has a 2-minute timeout to prevent blocking.
- **Abuse story regression update** — AS-03, AS-04, AS-05 upgraded from RESIDUAL RISK to PREVENTED following JWT+RBAC implementation.
- **ESLint false positives suppressed** — `security/detect-object-injection` on closed constant maps in `usePermissions.js`, `clinicOptions.js`, and `AppointmentsPanel.jsx`.
- **CRS tuning** split into two files: `01-clinic-exclusions.conf` (pre-CRS tx.* variables) and `02-clinic-rule-exclusions.conf` (post-CRS rule exclusions), loaded in the correct order via `modsecurity.conf`.
