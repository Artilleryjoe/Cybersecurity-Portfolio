# Work in progress!
# Security Scripts Toolkit

A collection of modular Python and Ansible-based scripts for reconnaissance, hardening, vulnerability scanning, and reporting. Built for educational purposes, portfolio demonstration, and authorized security assessments.

---

## Security Scripts Portfolio (Python)

This section includes custom Python scripts for reconnaissance, scanning, and reporting. Developed for practical security testing in controlled environments.

### Included Scripts

| Script Name             | Description                                                                 |
|-------------------------|-----------------------------------------------------------------------------|
| `shodan-scanner.py`     | Uses the Shodan API to scan hosts for exposed services and banners.        |
| `port_scanner.py`       | Custom TCP port scanner for specified ports.                               |
| `dns_enum.py`           | Enumerates DNS records and attempts zone transfers.                        |
| `who_geo.py`            | Performs Whois and GeoIP lookups on IPs or domains.                        |
| `cert_grabber.py`       | Retrieves SSL/TLS certificate information and expiration.                  |
| `meta_extract.py`       | Extracts metadata from files (images, PDFs, DOCX).                         |
| `vuln_check.py`         | Matches open ports and services to known CVEs.                             |
| `exploit_checker.py`    | Checks for common exploits (e.g., SMBv1, exposed RDP).                     |
| `email_head_tool.py`    | Analyzes email headers for SPF, DKIM, DMARC, and relay paths.              |
| `password_spray.py`     | Performs password spray attacks (test environments only, using Hydra).     |
| `markdown_gen.py`       | Generates clean Markdown summary reports.                                  |
| `csv_json_export.py`    | Exports scan results and data in CSV and JSON formats.                     |

---

## Ansible Hardening Playbooks

This section contains **Ansible playbooks** for automating system security hardening tasks. These are modular and reusable for secure deployments.

### Included Playbooks

| Playbook      | Description                                                                                     |
|-----------------|-------------------------------------------------------------------------------------------------|
| `ssh.yml`       | Hardens SSH server settings: disables root login, enforces key-only auth, restarts SSH service. |
| `users.yml`     | Manages user accounts, groups, SSH keys, and permissions.                                       |
| `fail2ban.yml`  |	Install and configure Fail2Ban with SSH jail.                                                   |
| `firewalls.yml` | Configure UFW firewall rules.                                                                   |


### Example Usage

```bash
ansible-playbook -i ansible-hardening/inventory/hosts.yml ansible-hardening/playbooks/ssh.yml --ask-become-pass
```
- Uses the inventory file in `ansible-hardening/inventory/hosts.yml`
- Edit this file to match your own server IP addresses

- Requires sshpass if using password-based auth

- Sudo password prompt appears unless SSH keys are configured with proper privileges

# Requirements
## Python Scripts
- Python: 3.8+

- Modules (install via pip install -r requirements.txt):

- requests, dnspython, python-docx, PyPDF2, shodan

- External Tools:

- exiftool

- hydra

- nmap (optional)

## Ansible Playbooks
- Ansible: 2.10+

## Required tools:

- sshpass (for password-based SSH connections)

- sudo (on target systems)

## Setup
```bash
# Clone the repo
git clone https://github.com/yourusername/security-scripts-toolkit.git
cd security-scripts-toolkit
```
# Set up Python virtual environment
```python3 -m venv venv
source venv/bin/activate
```
# Install Python dependencies
```pip install -r requirements.txt```
## Tested on:

 - Ubuntu 22.04 LTS

- Termux on Pixel 9a (tricky)

- Virtual Lab Environments (KVM/Docker/VMware/Vagrant)

## Top Master's Degree Labs

Below are ten standout labs from my cybersecurity master's degree program:

1. **Active Directory Security** – Hardening and attack simulation in a Windows AD environment.
2. **Incident Response Workflow** – Coordinated triage and forensic analysis on compromised hosts.
3. **Secure Coding Practices** – Remediating OWASP Top 10 vulnerabilities in sample applications.
4. **Cloud Penetration Testing** – Assessing IAM and network configurations in popular cloud services.
5. **Digital Forensics** – Disk and memory imaging, followed by artifact analysis.
6. **Malware Analysis Fundamentals** – Static and dynamic analysis of real malware samples.
7. **Web Application Attack & Defense** – Hands-on exploitation and patching of vulnerable web apps.
8. **Network Intrusion Detection** – Building and tuning a Snort/Suricata-based IDS lab.
9. **Threat Hunting with SIEM** – Using log data and queries to uncover suspicious activity.
10. **Wireless Security Assessment** – Auditing Wi-Fi networks and implementing mitigation strategies.

## Legal & Ethical Notice
This toolkit is intended for educational use, authorized testing, and professional development only.

Do not use these scripts or playbooks on networks or systems without explicit written permission.

Unauthorized use of security tools is illegal and unethical.
