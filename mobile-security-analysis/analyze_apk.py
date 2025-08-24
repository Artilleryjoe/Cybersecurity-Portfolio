#!/usr/bin/env python3
"""
Mobile Security Analysis Tool
Performs static analysis on Android APKs using apktool and JADX.

Usage:
    python analyze_apk.py path/to/app.apk [--out output_dir]
"""

import argparse
import shutil
import subprocess
from pathlib import Path


def run_tool(command, cwd=None):
    """Run an external command and stream its output."""
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[!] Command failed: {' '.join(command)}")
        if result.stderr:
            print(result.stderr)
    else:
        if result.stdout:
            print(result.stdout)
    return result.returncode


def decompile_apk(apk_path: str, out_dir: Path) -> int:
    """Decompile APK with apktool."""
    if shutil.which("apktool") is None:
        print("[!] apktool not found. Please install it first.")
        return 1
    out_dir.mkdir(parents=True, exist_ok=True)
    return run_tool(["apktool", "d", "-f", apk_path, "-o", str(out_dir)])


def jadx_decompile(apk_path: str, out_dir: Path) -> int:
    """Generate Java source using JADX."""
    if shutil.which("jadx") is None:
        print("[!] jadx not found. Please install it first.")
        return 1
    out_dir.mkdir(parents=True, exist_ok=True)
    return run_tool(["jadx", apk_path, "-d", str(out_dir)])


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Static APK analysis with apktool and JADX"
    )
    parser.add_argument("apk", help="Path to the target APK file")
    parser.add_argument(
        "--out", default="analysis_output", help="Directory to store results"
    )
    args = parser.parse_args()

    apk_path = Path(args.apk).resolve()
    output_dir = Path(args.out)

    print("[*] Decompiling with apktool…")
    decompile_apk(str(apk_path), output_dir / "apktool")

    print("[*] Decompiling with JADX…")
    jadx_decompile(str(apk_path), output_dir / "jadx")

    print("[*] Analysis complete.")


if __name__ == "__main__":
    main()
