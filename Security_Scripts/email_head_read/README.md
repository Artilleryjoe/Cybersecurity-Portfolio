# email_head_tool.py

## Purpose

Analyzes raw email files (.eml) to extract and report authentication results (SPF, DKIM, DMARC) and display key email headers for phishing and spoofing analysis.

## Features

- Parses raw email headers with proper decoding
- Extracts SPF, DKIM, DMARC results from Authentication-Results headers
- Displays key headers including From, To, Subject, Date, Message-ID, and Received
- Command-line tool accepting `.eml` files

## Requirements

- Python 3.x

## Installation

No external dependencies. Uses Python’s built-in `email` library.

## Usage

```bash
python3 email_head_tool.py -i suspicious_email.eml
Arguments
-i, --input – Path to the raw email file (.eml) to analyze
```
## Example Output
sql
Copy
Edit
SPF result: pass
DKIM result: fail
DMARC result: pass

## Key Headers:
`From: attacker@example.com
To: victim@example.com
Subject: Urgent account update required
Date: Wed, 23 Jul 2025 10:00:00 -0500
Message-ID: <1234567890@example.com>
Received: from unknown (HELO mail.example.com) (198.51.100.1)`

## Security Context
Intended for email forensic analysis and phishing investigations on emails you have received or are authorized to inspect.

License
MIT License. Use at your own risk.
