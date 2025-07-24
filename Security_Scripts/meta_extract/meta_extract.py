#!/usr/bin/env python3

import os
import sys
import argparse
import json
import subprocess

def extract_metadata(file_path):
    try:
        result = subprocess.run(
            ["exiftool", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            return {"file": file_path, "error": result.stderr.strip()}

        metadata = {}
        for line in result.stdout.strip().split("\n"):
            if ": " in line:
                key, value = line.split(": ", 1)
                metadata[key.strip()] = value.strip()
        return {"file": file_path, "metadata": metadata}
    except Exception as e:
        return {"file": file_path, "error": str(e)}

def main():
    parser = argparse.ArgumentParser(description="Extract metadata from files using exiftool.")
    parser.add_argument(
        "-f", "--files", nargs="+", required=True,
        help="List of files to extract metadata from."
    )
    parser.add_argument(
        "-o", "--output", default="metadata_results.json",
        help="Path to output JSON file."
    )
    args = parser.parse_args()

    results = []
    for file_path in args.files:
        if os.path.exists(file_path):
            results.append(extract_metadata(file_path))
        else:
            results.append({"file": file_path, "error": "File not found"})

    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)

    print(f"[+] Metadata written to {args.output}")

if __name__ == "__main__":
    main()
