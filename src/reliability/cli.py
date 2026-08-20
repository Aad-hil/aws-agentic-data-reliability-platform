"""Command-line entry point for local reliability analysis."""

from __future__ import annotations

import argparse

from .runner import run_reliability_checks


def main() -> None:
    parser = argparse.ArgumentParser(description="Run data reliability checks on a CSV dataset.")
    parser.add_argument("csv_path", help="Path to the CSV dataset")
    args = parser.parse_args()

    report = run_reliability_checks(args.csv_path)
    print(f"Dataset: {report.dataset.name}")
    print(f"Rows: {report.dataset.row_count}")
    print(f"Findings: {report.finding_count}")
    print()
    for finding in report.findings:
        location = f" [{finding.column}]" if finding.column else ""
        print(f"- {finding.severity.value.upper()}: {finding.description}{location}")
        print(f"  Evidence: {finding.evidence}")
