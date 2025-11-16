# Ansible Hardening Toolkit

A collection of modular Ansible playbooks and inventory files to automate security hardening, monitoring, and lifecycle management for Linux hosts.

---

## Inventory & Configuration

- `inventory/hosts.yml` — Defines target hosts grouped by platform (`linux_debian`, `linux_rhel`) and a `servers` parent group.
- `group_vars/all.yml` — Centralizes opinionated defaults (users to provision, firewall rules, sysctl tunables, logging endpoints, etc.). Override as needed in environment-specific vars.
- `ansible.cfg` — Sets sensible defaults such as inventory path, privilege escalation, and safe output formatting.

---

## Playbooks

| Playbook           | Description                                                        |
|--------------------|--------------------------------------------------------------------|
| `baseline.yml`     | Applies core OS hardening (packages, sysctl, banners, services).    |
| `users.yml`        | Manages privileged users, groups, and SSH authorized keys.          |
| `firewalls.yml`    | Configures UFW policies/allow rules using structured variables.     |
| `ssh.yml`          | Enforces hardened `sshd_config` parameters.                         |
| `fail2ban.yml`     | Installs Fail2Ban and templates custom jails.                       |
| `logging.yml`      | Sets up rsyslog forwarding and Filebeat telemetry.                  |
| `monitoring.yml`   | Deploys auditd + AIDE for host-based intrusion detection.           |
| `patching.yml`     | Executes controlled OS updates within a maintenance window.         |
| `site.yml`         | Convenience wrapper that imports the full suite sequentially.       |

---

## Usage

Run playbooks with:

```bash
ansible-playbook playbooks/<playbook>.yml --ask-become-pass

- Run `ansible-playbook playbooks/site.yml` to orchestrate the entire automation stack.
- To use the firewall role, install the supporting collection once: `ansible-galaxy collection install community.general`.
```
- Replace <playbook> with the desired playbook filename.

## Requirements
- Ansible 2.16+

- Python 3.8+

- SSH key access to target hosts

- Sudo privileges on target hosts

## Notes
All playbooks use become: yes for privilege escalation.

Inventory and playbooks are modular and extensible for future additions.

Use responsibly and only on systems you own or have explicit permission to manage.

## Folder Structure
```
ansible-hardening/
├── ansible.cfg
├── group_vars/
│   └── all.yml
├── inventory/
│   └── hosts.yml
├── playbooks/
│   ├── baseline.yml
│   ├── fail2ban.yml
│   ├── firewalls.yml
│   ├── logging.yml
│   ├── monitoring.yml
│   ├── patching.yml
│   ├── site.yml
│   ├── ssh.yml
│   └── users.yml
└── README.md
```
## Author

Kristopher McCoy  
Cybersecurity Professional | Portfolio Project — July 2025  
GitHub: [github.com/artilleryjoe](https://github.com/artilleryjoe)
