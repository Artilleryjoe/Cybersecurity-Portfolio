# User Guide

This guide walks through each vulnerability module in the portfolio and explains how to explore them safely so the material can support training and defensive research.

## Security Scripts Toolkit

### `shodan-scanner.py`
- **Walkthrough:** Provide a list of IP addresses, then run the script to retrieve service banners and Shodan vulnerability data.
- **Learning Objective:** Understand how exposed services reveal attack surface information.

### `vuln_check.py`
- **Walkthrough:** Feed the script port scan results to match services against known CVEs.
- **Learning Objective:** Learn to map discovered services to public vulnerabilities.

### `exploit_checker.py`
- **Walkthrough:** Supply service versions and review the reported potential exploits.
- **Learning Objective:** Practice validating exploitability before pursuing remediation.

### Safety Disclaimer
Use these scripts only on systems you own or have explicit written permission to test. Unauthorized scanning is illegal and unethical.

## SecurityAwarenessApp Modules

### `vulns.storage.InsecurePrefsActivity`
- **Walkthrough:** Enter sample data to see how plain‑text SharedPreferences can expose sensitive information.
- **Learning Objective:** Recognize the risks of insecure local storage and the value of encryption.

### `vulns.auth.WeakPasswordActivity`
- **Walkthrough:** Try common weak passwords to observe how the app accepts them.
- **Learning Objective:** Appreciate the need for strong password policies and input validation.

### `vulns.network.InsecureHttpActivity`
- **Walkthrough:** Trigger a network call and monitor traffic to witness unencrypted HTTP requests.
- **Learning Objective:** See why HTTPS is essential for protecting data in transit.

### Safety Disclaimer
Run the mobile app, now available at [YourOrg/mobile-app](https://github.com/YourOrg/mobile-app), in an isolated lab environment. Do not transmit real personal or business data through these modules.

---

By experimenting with these modules, learners gain practical insight into finding and mitigating vulnerabilities while preserving the safety and reputation of the organizations they support.
