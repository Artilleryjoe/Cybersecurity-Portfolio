# password_spray.py

## Purpose

Simulates a password spray attack using one password across many usernames, targeting a single login endpoint. This script is designed for **defensive testing, education, and red team lab use only**.

## ⚠ Ethical and Legal Warning

> This tool is for use only on systems you own or have explicit, written authorization to test.
> Unauthorized use of this tool **may be illegal** and violates responsible security testing practices.

By default, the script operates in `--dry-run` mode and **will not make real login attempts** unless explicitly allowed via `--live`.

## Features

- Dry-run mode by default (safe testing)
- One password tested across multiple usernames (spray pattern)
- Rate-limited (3 seconds default)
- Simple POST-based login form support

## Requirements

- Python 3.x
- `requests` library (`pip install requests`)

## Installation

```bash
pip install requests
```
## Usage
```bash
python3 password_spray.py -u users.txt -p "Spring2024!" -t http://target.local/login
```
## Live mode (real requests):
```bash
python3 password_spray.py -u users.txt -p "Spring2024!" -t http://target.local/login --live
```
## Arguments
`-u`, --userfile – File with usernames (one per line)

`-p`, --password – The password to spray

`-t`, --target – Login form URL to POST to

`--delay` – Seconds to wait between attempts (default: 3)

`--live` – Actually perform the spray (default is dry-run)

## Example Input (users.txt)
```pgsql
jane.doe
john.smith
admin
```
## Security Context
This tool demonstrates password hygiene risks in corporate networks, especially where accounts share weak or default credentials. Ensure multi-factor authentication (MFA), strong password policies, and monitoring are in place to prevent real password spray attacks.

## License
MIT License. Use responsibly.
