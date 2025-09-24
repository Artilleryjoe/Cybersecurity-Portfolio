# Iron Dillo Cybersecurity Portfolio

Iron Dillo Cybersecurity is a veteran-owned security partner supporting individuals, small businesses, and rural operations throughout East Texas. This repository powers the public-facing site, documents research, and shares automation that keeps our clients resilient.

## Table of Contents
- [Mission & Focus](#mission--focus)
- [Portfolio Highlights](#portfolio-highlights)
- [Quick Start](#quick-start)
- [Project Summaries](#project-summaries)
- [Learning Resources](#learning-resources)
- [Contact](#contact)
- [Legal & Ethical Notice](#legal--ethical-notice)

## Mission & Focus
- Deliver clarity, speed, and trustworthy cybersecurity support tailored to Lindale, Tyler, and neighboring communities.
- Combine battle-tested processes with automation to harden systems, monitor threats, and lead confident response efforts.
- Share open resources that help rural teams elevate their defenses without sacrificing uptime.

## Portfolio Highlights
| Directory | Description |
| --- | --- |
| `docs/` | Source for the GitHub Pages site, including the Iron Dillo brand, services overview, and research highlights. |
| `Security_Scripts/` | Python utilities for reconnaissance, vulnerability analysis, and reporting. |
| `ansible-hardening/` | Modular Ansible roles and playbooks for SSH, user, firewall, and Fail2Ban hardening. |
| `security-dashboard/` | Dockerized Elastic Stack deployment that powers our monitoring and visualization toolkit. |
| `custom-ids/` | Experiments in intrusion detection rules and tuning. |
| `mobile-security-analysis/` | Assets and notes supporting the Android security analysis toolkit. |
| `quantum-computing/` | Research artifacts exploring post-quantum and quantum-assisted security concepts. |
| `blockchain-secure-logging/` | Prototype of a tamper-evident audit logging system built on a private blockchain network. |

## Quick Start
Most assets rely on standard Python, Docker, and Ansible tooling. After cloning the repository, install Git LFS to retrieve large PNG resources used in documentation:

```bash
git lfs install
git lfs pull
```

Explore each project directory for detailed setup instructions, runtime requirements, and usage notes.

### Recommended Tooling
- Python 3.10+
- Docker Desktop or a compatible container runtime
- Ansible 2.13+
- Git LFS 3.x

## Project Summaries
### Automation & Infrastructure
- **`ansible-hardening/`** – Harden SSH, user accounts, firewall rules, and Fail2Ban policies with reusable roles and playbooks.
- **`Security_Scripts/`** – Execute reconnaissance, vulnerability scanning, and reporting tasks with portable Python utilities.
- **`security-dashboard/`** – Launch a monitoring stack with Docker Compose to visualize telemetry and security alerts.
- **`blockchain-secure-logging/`** – Demonstrates tamper-evident logging using a private Ganache chain and smart contracts.

### Detection & Response
- **`custom-ids/`** – Prototype intrusion detection rules, threshold tuning, and alert workflows tailored to rural environments.
- **`mobile-security-analysis/`** – Documentation, scripts, and datasets that support Android-focused investigations and training labs.

### Research & Training
- **`docs/`** – Source files for the GitHub Pages site, including service descriptions, methodology breakdowns, and downloadable assets.
- **`quantum-computing/`** – Quantum security experiments such as [QRNG-Based Steganography](quantum-computing/QRNGSteganography.md) and the [QAOA Max-Cut tutorial](quantum-computing/QAOAMaxCut.md).

## Learning Resources
- [User Guide](docs/UserGuide.md) – Learn how to explore the security scripts and mobile lab safely.
- [Teacher Guide](docs/TeacherGuide.md) – Classroom facilitation notes for the included training modules.
- [Blockchain-Based Secure Logging System](docs/BlockchainLogging.md) – Prototype for tamper-evident audit trails using a private Ganache chain.

## Contact
- Website: [irondillocybersecurity.com](https://www.irondillo.com)

## Legal & Ethical Notice
This portfolio is intended for authorized security research, education, and professional development. Only run the included tools and playbooks on systems you own or have explicit written permission to test. Unauthorized use is illegal and unethical.
