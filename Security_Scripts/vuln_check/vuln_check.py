#!/usr/bin/env python3

def generate_markdown_report(data):
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
        lines.append("")  # Add blank line for spacing
    return "\n".join(lines)

def save_report(markdown_str, filename="report.md"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(markdown_str)
    print(f"[+] Report saved as {filename}")

if __name__ == "__main__":
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
