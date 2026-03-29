#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path


SEVERITY_ORDER = {"High": 0, "Medium": 1, "Low": 2, "Informational": 3}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Compare two ZAP JSON reports and report newly introduced alert types."
    )
    parser.add_argument("--base", required=True, help="Path to the baseline ZAP JSON report")
    parser.add_argument("--head", required=True, help="Path to the PR/head ZAP JSON report")
    parser.add_argument("--base-label", required=True, help="Label for the baseline scan")
    parser.add_argument("--head-label", required=True, help="Label for the head scan")
    parser.add_argument("--markdown", required=True, help="Output markdown summary path")
    parser.add_argument("--json", required=True, help="Output JSON diff path")
    parser.add_argument(
        "--fail-on-severity",
        action="append",
        default=[],
        choices=["High", "Medium", "Low", "Informational"],
        help="Fail if newly introduced alert types of this severity exist. May be specified multiple times.",
    )
    return parser.parse_args()


def parse_severity(alert):
    for candidate in (alert.get("risk"), alert.get("riskdesc")):
        if not candidate:
            continue

        severity = str(candidate).split(" ", 1)[0].strip()
        if severity == "Info":
            return "Informational"
        if severity in SEVERITY_ORDER:
            return severity

    return "Informational"


def load_report(path_str):
    path = Path(path_str)
    return json.loads(path.read_text()), path


def normalize_report(report):
    alert_types = {}
    for site in report.get("site", []):
        site_name = site.get("@name") or site.get("name") or "unknown-site"
        for alert in site.get("alerts", []):
            severity = parse_severity(alert)
            key = (
                alert.get("pluginid") or "unknown-plugin",
                alert.get("name") or "Unknown alert",
                severity,
            )
            item = alert_types.setdefault(
                key,
                {
                    "pluginid": key[0],
                    "name": key[1],
                    "severity": severity,
                    "instances": 0,
                    "sites": set(),
                },
            )

            item["sites"].add(site_name)
            instances = alert.get("instances") or []
            if isinstance(instances, list):
                item["instances"] += len(instances)
            else:
                item["instances"] += 1

    normalized = {}
    for key, item in alert_types.items():
        normalized[key] = {
            **item,
            "sites": sorted(item["sites"]),
        }
    return normalized


def count_by_severity(items):
    counts = {severity: 0 for severity in SEVERITY_ORDER}
    for item in items:
        counts[item["severity"]] = counts.get(item["severity"], 0) + 1
    return counts


def sort_alerts(items):
    return sorted(
        items,
        key=lambda item: (
            SEVERITY_ORDER.get(item["severity"], 99),
            -item["instances"],
            item["name"],
        ),
    )


def render_counts_table(title, counts):
    total = sum(counts.values())
    lines = [
        f"### {title}",
        "",
        "| Severity | Count |",
        "| --- | ---: |",
        f"| High | {counts.get('High', 0)} |",
        f"| Medium | {counts.get('Medium', 0)} |",
        f"| Low | {counts.get('Low', 0)} |",
        f"| Informational | {counts.get('Informational', 0)} |",
        f"| Total | {total} |",
    ]
    return lines


def render_alerts_table(title, items):
    lines = [f"### {title}", ""]
    if not items:
        lines.append("None.")
        return lines

    lines.extend(
        [
            "| Alert | Severity | Instances | Sites |",
            "| --- | --- | ---: | --- |",
        ]
    )
    for item in sort_alerts(items):
        sites = ", ".join(item["sites"])
        lines.append(
            f"| {item['name']} | {item['severity']} | {item['instances']} | {sites} |"
        )
    return lines


def main():
    args = parse_args()
    base_report, base_path = load_report(args.base)
    head_report, head_path = load_report(args.head)

    base_alerts = normalize_report(base_report)
    head_alerts = normalize_report(head_report)

    base_keys = set(base_alerts)
    head_keys = set(head_alerts)

    new_alerts = [head_alerts[key] for key in sorted(head_keys - base_keys)]
    resolved_alerts = [base_alerts[key] for key in sorted(base_keys - head_keys)]
    persistent_alerts = [head_alerts[key] for key in sorted(head_keys & base_keys)]

    new_counts = count_by_severity(new_alerts)
    resolved_counts = count_by_severity(resolved_alerts)
    persistent_counts = count_by_severity(persistent_alerts)

    fail_severities = set(args.fail_on_severity)
    blocking_alerts = [
        item for item in new_alerts if item["severity"] in fail_severities
    ]

    markdown_lines = [
        "## DAST PR Comparison",
        "",
        f"- Baseline scan: `{args.base_label}`",
        f"- PR scan: `{args.head_label}`",
        f"- Baseline report: `{base_path.name}`",
        f"- PR report: `{head_path.name}`",
    ]

    if fail_severities:
        markdown_lines.append(
            f"- Gate: fail on newly introduced `{', '.join(sorted(fail_severities, key=SEVERITY_ORDER.get))}` alert types."
        )

    markdown_lines.extend([""])
    markdown_lines.extend(render_counts_table("New Alert Types", new_counts))
    markdown_lines.extend([""])
    markdown_lines.extend(render_alerts_table("Newly Introduced Alerts", new_alerts))
    markdown_lines.extend([""])
    markdown_lines.extend(render_counts_table("Resolved Alert Types", resolved_counts))
    markdown_lines.extend([""])
    markdown_lines.extend(render_alerts_table("Resolved Alerts", resolved_alerts))
    markdown_lines.extend([""])
    markdown_lines.extend(render_counts_table("Persistent Alert Types", persistent_counts))

    Path(args.markdown).write_text("\n".join(markdown_lines) + "\n")

    output = {
        "base_label": args.base_label,
        "head_label": args.head_label,
        "new_alerts": new_alerts,
        "resolved_alerts": resolved_alerts,
        "persistent_alert_counts": persistent_counts,
        "new_alert_counts": new_counts,
        "resolved_alert_counts": resolved_counts,
        "blocking_alerts": blocking_alerts,
        "blocking_fail_severities": sorted(fail_severities, key=SEVERITY_ORDER.get),
    }
    Path(args.json).write_text(json.dumps(output, indent=2) + "\n")

    print("\n".join(markdown_lines))

    if blocking_alerts:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
