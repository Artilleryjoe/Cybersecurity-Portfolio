
#!/usr/bin/env python3
"""Generate Markdown (and optional HTML) reports from structured scan data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:  # Optional dependency for HTML output
    import markdown as markdown_lib
except Exception:  # pragma: no cover - optional
    markdown_lib = None


def render_value(value: Any, indent: int = 0) -> str:
    prefix = " " * indent + "- "
    if isinstance(value, dict):
        lines = []
        for key, nested in value.items():
            lines.append(f"{prefix}**{key}**:")
            lines.append(render_value(nested, indent + 4))
        return "\n".join(lines)
    if isinstance(value, list):
        lines = []
        for item in value:
            lines.append(prefix + str(item))
        return "\n".join(lines)
    return prefix + str(value)


def generate_markdown_report(data: dict, title: str = "Scan Report") -> str:
    lines = [f"# {title}\n"]
    for section, contents in data.items():
        lines.append(f"## {section}\n")
        lines.append(render_value(contents))
        lines.append("")
    return "\n".join(lines)


def save_report(markdown_str: str, filename: Path) -> None:
    filename.parent.mkdir(parents=True, exist_ok=True)
    filename.write_text(markdown_str, encoding="utf-8")
    print(f"[+] Report saved as {filename}")


def convert_to_html(markdown_str: str) -> str:
    if markdown_lib is None:
        raise SystemExit("Install the 'markdown' package to export HTML reports")
    return markdown_lib.markdown(markdown_str)


def load_data(path: Path | None):
    if not path:
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Markdown/HTML reports from JSON data")
    parser.add_argument('-i', '--input', type=Path, help="Path to JSON data file")
    parser.add_argument('-o', '--output', type=Path, default=Path('report.md'), help="Markdown output path")
    parser.add_argument('--title', default='Scan Report', help="Report title")
    parser.add_argument('--html', type=Path, help="Optional HTML output path")

    args = parser.parse_args()

    data = load_data(args.input)
    if not data:
        sample = {
            "Host Info": {"IP": "192.168.1.1", "Hostname": "example.local"},
            "Open Ports": [22, 80, 443],
            "Vulnerabilities": ["CVE-2021-41773", "CVE-2021-42013"],
        }
        data = sample

    markdown_report = generate_markdown_report(data, title=args.title)
    save_report(markdown_report, args.output)

    if args.html:
        html = convert_to_html(markdown_report)
        args.html.parent.mkdir(parents=True, exist_ok=True)
        args.html.write_text(html, encoding='utf-8')
        print(f"[+] HTML report saved as {args.html}")


if __name__ == "__main__":
    main()
