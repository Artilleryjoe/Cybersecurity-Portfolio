#!/usr/bin/env python3

import argparse
import csv
import json
import os
import sys
from typing import Any, Dict, Iterable, List

def load_input_data(input_file):
    if input_file:
        with open(input_file, 'r') as f:
            data = json.load(f)
    else:
        # Read from stdin
        data = json.load(sys.stdin)
    return data


def flatten_record(record: Dict[str, Any], parent_key: str = "", sep: str = ".") -> Dict[str, Any]:
    """Flatten nested dictionaries/lists so that CSV export stays tidy."""

    items: Dict[str, Any] = {}
    for key, value in record.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else str(key)
        if isinstance(value, dict):
            items.update(flatten_record(value, new_key, sep=sep))
        elif isinstance(value, list):
            if value and all(isinstance(elem, dict) for elem in value):
                for idx, elem in enumerate(value):
                    items.update(flatten_record(elem, f"{new_key}[{idx}]", sep=sep))
            else:
                items[new_key] = ", ".join(map(str, value))
        else:
            items[new_key] = value
    return items

def export_json(data, output_file, pretty=True):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4 if pretty else None)
    print(f"[+] Exported JSON to {output_file}")

def export_csv(data, output_file, *, flatten=False, fields: Iterable[str] | None = None):
    if not isinstance(data, list):
        print("[-] Error: CSV export requires a list of dictionaries.")
        return

    rows: List[Dict[str, Any]] = []
    for entry in data:
        if not isinstance(entry, dict):
            print("[-] CSV export skipped non-dictionary entry")
            continue
        rows.append(flatten_record(entry) if flatten else entry)

    if not rows:
        print("[-] No structured data to export as CSV")
        return

    fieldnames = list(fields) if fields else sorted({key for row in rows for key in row.keys()})
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"[+] Exported CSV to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Export recon data to CSV and/or JSON.")
    parser.add_argument('-i', '--input', help="Input JSON file (or use stdin)")
    parser.add_argument('-o', '--output', help="Base output filename (no extension)")
    parser.add_argument('-f', '--format', choices=['csv', 'json', 'both'], default='both', help="Output format")
    parser.add_argument('--flatten', action='store_true', help="Flatten nested structures for CSV")
    parser.add_argument('--fields', nargs='+', help="Explicit CSV column ordering")
    parser.add_argument('--dedupe', action='store_true', help="Remove duplicate records before exporting")
    parser.add_argument('--compact-json', action='store_true', help="Emit JSON without whitespace")

    args = parser.parse_args()
    data = load_input_data(args.input)

    base_filename = args.output or (os.path.splitext(args.input)[0] if args.input else 'output')

    if args.dedupe and isinstance(data, list):
        seen = set()
        deduped = []
        for entry in data:
            marker = json.dumps(entry, sort_keys=True)
            if marker in seen:
                continue
            seen.add(marker)
            deduped.append(entry)
        data = deduped

    if args.format in ['json', 'both']:
        export_json(data, base_filename + '.json', pretty=not args.compact_json)

    if args.format in ['csv', 'both']:
        export_csv(data, base_filename + '.csv', flatten=args.flatten, fields=args.fields)

if __name__ == "__main__":
    main()
