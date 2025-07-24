#!/usr/bin/env python3
"""
markdown_html_gen.py
Generate Markdown reports from structured scan data and optionally convert to HTML.
"""

import os

def generate_markdown_report(data):
    """
    Generate a Markdown string from a nested dictionary/list structure.
    """
    lines = ["# Scan Report\n"]
    for section, contents in data.items():
        lines.append(f"## {section}\n")
        if isinstance(contents, dict):
            for key, value in contents.items():
                lines.append(f"- **{key}**: {value}")
        elif isinstance(contents, list):
            for item in contents:
                lines.append(f"- {item}")
        else:
            lines.append(str(contents))
        lines.append("")  # Blank line for spacing
    return "\n".join(lines)

def save_report(markdown_str, filename="report.md"):
    """
    Save the Markdown string to a file.
    """
    with open(filename, "w", encoding="utf-8") as f:
        f.write(markdown_str)
    print(f"[+] Report saved as {filename}")

# Optional: HTML conversion if you want to add it
# Uncomment if you have the `markdown` package installed
#
# import markdown
# def convert_to_html(markdown_str):
#     """
#     Convert Markdown string to HTML.
#     """
#     return markdown.markdown(markdown_str)
#
# def save_html(html_str, filename="report.html"):
#     """
#     Save the HTML string to a file.
#     """
#     with open(filename, "w", encoding="utf-8") as f:
#         f.write(html_str)
#     print(f"[+] HTML report saved as {filename}")

def main():
    sample_data = {
        "Host Info": {
            "IP": "192.168.1.1",
            "Hostname": "example.local"
        },
        "Open Ports": [22, 80, 443],
        "Vulnerabilities": [
            "CVE-2021-41773",
            "CVE-2021-42013"
        ]
    }

    markdown_report = generate_markdown_report(sample_data)
    save_report(markdown_report)

    # Optional HTML generation
    # html_report = convert_to_html(markdown_report)
    # save_html(html_report)

if __name__ == "__main__":
    main()
