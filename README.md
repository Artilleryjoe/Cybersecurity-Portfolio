# Iron Dillo Cybersecurity Portfolio

Veteran-owned cybersecurity for East Texas small businesses, individuals, and rural operations. This repository showcases small projects for security automation, hardening, and monitoring, combining Python utilities, Ansible playbooks, and a Kibana-based dashboard for visualizing scan data.

## Repository Overview

- **Security_Scripts/** – Collection of Python tools for reconnaissance, vulnerability checks, and reporting.
- **ansible-hardening/** – Modular Ansible playbooks to secure servers (SSH, users, firewall, Fail2Ban).
- **security-dashboard/** – Dockerized Elastic Stack project exposing a Kibana security dashboard.

See each directory's README for detailed usage.

## Getting Started

After cloning the repository, initialize Git LFS to fetch PNG assets and explore each project directory for setup details.

```bash
git lfs install
git lfs pull
```

## Large Files

PNG assets are tracked with Git LFS. To download these images after cloning, run:

```bash
git lfs install
git lfs pull
```


## Service Areas

Based in East Texas, Iron Dillo Cybersecurity proudly supports individuals, small businesses, and rural operations with emphasis on the communities of **Lindale** and **Tyler**.

## Documentation

- [User Guide](docs/UserGuide.md)
- [Teacher Guide](docs/TeacherGuide.md)

## Research Projects

- [QRNG-Based Steganography Experiment](docs/QRNGSteganography.md)


## Advanced Penetration Testing Toolkit

- **Scope:** Automate and enhance exploit testing.
- **Tools:** Python, Metasploit.
- **Implementation:** Automate common attack patterns and integrate stealth and evasion techniques.
- **Challenges:** Keeping the toolkit updated; ethical and legal considerations.
- **Next Steps:** Add machine learning modules; design a GUI.
- **Resources:** [Metasploit Documentation](https://docs.metasploit.com/)


## Mobile Security Analysis Tool for Android

- **Scope:** Analyze APKs for static and dynamic flaws.
- **Tools:** JADX, APKTool, Frida, Python.
- **Implementation:** Decompile apps, write automated analysis scripts, perform live testing.
- **Challenges:** Obfuscation, anti-debugging, code scalability.
- **Next Steps:** Automate and chain analysis tasks; expand to iOS.
- **Resources:** [JADX](https://github.com/skylot/jadx)


## Custom Intrusion Detection System (IDS)

- **Scope:** Detect threats via custom network rules.
- **Tools:** Snort, Suricata.
- **Implementation:** Install and configure IDS, write custom rule sets, and simulate attack scenarios.
- **Challenges:** Tuning false positives, managing high-volume traffic.
- **Next Steps:** Integrate with SIEM, pair with anomaly detection.
- **Resources:** [Snort Documentation](https://www.snort.org/documents)

## Upcoming Prototype

### Blockchain-Based Secure Logging System

- **Scope:** Build tamper-evident logs using blockchain.
- **Tools:** Ganache, Python.
- **Implementation:** Deploy a private blockchain and hash and commit logs as transactions.
- **Challenges:** Throughput, blockchain bloat, long-term storage.
- **Next Steps:** Integrate into systems and explore quantum-resilient chains.
- **Resources:** [Ganache](https://www.trufflesuite.com/ganache)


## Top Master's Degree Labs

Below are ten standout labs from my cybersecurity master's program:

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

## Contributing

Feedback and contributions are welcome. Open an issue or submit a pull request to help enhance these projects.

## Legal & Ethical Notice

This portfolio is intended for educational use, authorized testing, and professional development only. Do not run these tools or playbooks on networks or systems without explicit written permission. Unauthorized use of security tools is illegal and unethical.

