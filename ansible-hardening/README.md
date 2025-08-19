# Iron Dillo Ansible Toolkit

A collection of modular Ansible playbooks and inventory files to automate security hardening and system management for Iron Dillo Cybersecurity.

---

## Inventory

- `inventory/hosts.yml` — Defines target hosts and connection variables. Supports SSH key and sudo access. Includes a sample `[servers]` group with Lindale and Tyler hosts; update with your own systems.

---

## Playbooks

| Playbook         | Description                                            |
|------------------|--------------------------------------------------------|
| `users.yml`      | Manage users, groups, and SSH authorized keys.         |
| `firewalls.yml`  | Configure UFW firewall rules.                           |
| `ssh.yml`        | Harden SSH server configuration.                        |
| `fail2ban.yml`   | Install and configure Fail2Ban with SSH jail.           |

---

## Usage

Run playbooks with:

```bash
ansible-playbook -i inventory/hosts.yml playbooks/<playbook>.yml --ask-become-pass
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
├── inventory/
│   └── hosts.yml
├── playbooks/
│   ├── users.yml
│   ├── firewalls.yml
│   ├── ssh.yml
│   └── fail2ban.yml
└── README.md
```
## Author

Kristopher McCoy  
Cybersecurity Professional | Portfolio Project — July 2025  
GitHub: [github.com/artilleryjoe](https://github.com/artilleryjoe)
