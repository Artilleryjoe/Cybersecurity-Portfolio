#!/usr/bin/env python3

#!/usr/bin/env python3

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import List

SENSITIVE_KEYS = ("GPS", "Author", "Serial Number", "Software", "Creator")


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
        metadata.update(compute_hashes(file_path))
        metadata["sensitive_findings"] = [k for k in metadata if any(tag in k for tag in SENSITIVE_KEYS)]
        return {"file": file_path, "metadata": metadata}
    except Exception as e:
        return {"file": file_path, "error": str(e)}

def compute_hashes(file_path: str) -> dict:
    sha256 = hashlib.sha256()
    size = 0
    with open(file_path, 'rb') as fh:
        while True:
            chunk = fh.read(65536)
            if not chunk:
                break
            size += len(chunk)
            sha256.update(chunk)
    return {"sha256": sha256.hexdigest(), "size_bytes": size}


def collect_targets(paths: List[str], recursive: bool) -> List[str]:
    discovered: List[str] = []
    for entry in paths:
        path = Path(entry)
        if path.is_dir() and recursive:
            for candidate in path.rglob('*'):
                if candidate.is_file():
                    discovered.append(str(candidate))
        elif path.is_file():
            discovered.append(str(path))
        else:
            discovered.append(str(path))
    return discovered


def main():
    parser = argparse.ArgumentParser(description="Extract metadata from files using exiftool.")
    parser.add_argument(
        "-f", "--files", nargs="+", required=True,
        help="List of files or directories to extract metadata from."
    )
    parser.add_argument(
        "-o", "--output", default="metadata_results.json",
        help="Path to output JSON file."
    )
    parser.add_argument("-r", "--recursive", action="store_true", help="Recurse into directories")
    args = parser.parse_args()

    targets = collect_targets(args.files, args.recursive)
    results = []
    for file_path in targets:
        if os.path.exists(file_path):
            results.append(extract_metadata(file_path))
        else:
            results.append({"file": file_path, "error": "File not found"})

    with open(args.output, "w", encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"[+] Metadata written to {args.output}")

if __name__ == "__main__":
    main()
