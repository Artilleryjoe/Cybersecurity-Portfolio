# Iron Dillo Cybersecurity Portfolio

Iron Dillo Cybersecurity is a veteran-owned partner protecting individuals, small businesses, and rural operations throughout East Texas. This repository powers the public website, showcases automation projects, and documents research that keeps our clients resilient.

## Mission
- Deliver clarity, speed, and trustworthy cybersecurity support tailored to Lindale, Tyler, and neighboring communities.
- Combine battle-tested processes with automation to harden systems, monitor threats, and lead confident response efforts.
- Share open resources that help rural teams elevate their defenses without sacrificing uptime.

## Service Areas
- **Individuals & Families** – Personal device hardening, identity protection, and safety coaching.
- **Small Businesses** – Managed defense for retail, clinics, professional services, and makers.
- **Rural Operations** – Security for farms, co-ops, utilities, and remote infrastructure.

## Repository Overview
| Directory | Description |
| --- | --- |
| `docs/` | Source for the GitHub Pages site, including the Iron Dillo brand, services overview, and research highlights. |
| `Security_Scripts/` | Python utilities for reconnaissance, vulnerability analysis, and reporting. |
| `ansible-hardening/` | Modular Ansible roles and playbooks for SSH, user, firewall, and Fail2Ban hardening. |
| `security-dashboard/` | Dockerized Elastic Stack deployment that powers our monitoring and visualization toolkit. |
| `custom-ids/` | Experiments in intrusion detection rules and tuning. |
| `mobile-security-analysis/` | Assets and notes supporting the Android security analysis toolkit. |
| `Quantum Computing/` | Research artifacts exploring post-quantum and quantum-assisted security concepts. |

## Featured Resources
- [User Guide](docs/UserGuide.md) – Learn how to explore the security scripts and mobile lab safely.
- [Teacher Guide](docs/TeacherGuide.md) – Classroom facilitation notes for the included training modules.
- [Blockchain-Based Secure Logging System](docs/BlockchainLogging.md) – Prototype for tamper-evident audit trails using a private Ganache chain.
- [QRNG-Based Steganography Experiment](Quantum%20Computing/QRNGSteganography.md) – Research into quantum randomness for covert communication.

## Getting Started
Most assets rely on standard Python, Docker, and Ansible tooling. After cloning the repository, install Git LFS to retrieve large PNG resources used in documentation:

```bash
git lfs install
git lfs pull
```

Explore each project directory for specific setup instructions and usage notes.

## Contact
- Website: [irondillocybersecurity.com](https://irondillocybersecurity.com)
- Email: [security@irondillocyber.com](mailto:security@irondillocyber.com)
- Phone: 903-555-1234 (East Texas response line)

## Legal & Ethical Notice
This portfolio is intended for authorized security research, education, and professional development. Only run the included tools and playbooks on systems you own or have explicit written permission to test. Unauthorized use is illegal and unethical.
