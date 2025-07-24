#!/usr/bin/env python3

import argparse
import json
import csv
import os
import sys

def load_input_data(input_file):
    if input_file:
        with open(input_file, 'r') as f:
            data = json.load(f)
    else:
        # Read from stdin
        data = json.load(sys.stdin)
    return data

def export_json(data, output_file):
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"[+] Exported JSON to {output_file}")

def export_csv(data, output_file):
    if not isinstance(data, list):
        print("[-] Error: CSV export requires a list of dictionaries.")
        return

    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print(f"[+] Exported CSV to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Export recon data to CSV and/or JSON.")
    parser.add_argument('-i', '--input', help="Input JSON file (or use stdin)")
    parser.add_argument('-o', '--output', help="Base output filename (no extension)")
    parser.add_argument('-f', '--format', choices=['csv', 'json', 'both'], default='both', help="Output format")

    args = parser.parse_args()
    data = load_input_data(args.input)

    base_filename = args.output or (os.path.splitext(args.input)[0] if args.input else 'output')

    if args.format in ['json', 'both']:
        export_json(data, base_filename + '.json')

    if args.format in ['csv', 'both']:
        export_csv(data, base_filename + '.csv')

if __name__ == "__main__":
    main()
