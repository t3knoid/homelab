---
title: "Ansible Directory Structure & Conventions"
---

# Ansible Directory Structure & Conventions

## Overview
This document provides a detailed reference for the organization of the Ansible repository. It explains the purpose of each directory, outlines naming conventions, and includes a visual diagram to help contributors quickly understand the hierarchy.

---

## Top-Level Files
| File | Purpose |
|------|---------|
| `README.md` | Project overview and usage instructions |
| `all.yml` | Global variables applied across inventories and playbooks |
| `ansible.cfg` | Core Ansible configuration (defaults, paths, privilege escalation) |
| `dynamic_inventory.py` | Script for generating dynamic inventory data |
| `generate_role_docs.py` | Utility to auto-generate documentation for roles |

---

## Key Directories
| Directory | Purpose |
|-----------|---------|
| `filter_plugins/` | Custom Jinja2 filters for inventory and playbook logic |
| `inventory/` | Environment- and service-specific inventories (e.g., `dns`, `grafana`, `jenkins`) |
| `playbooks/` | Task orchestration grouped by service or platform |
| `roles/` | Modular building blocks for automation (service-specific setups) |
| `roles/global/` | Shared tasks and variables used across multiple roles |
| `roles/users/` | User and group management tasks |

---

## Examples
- **Inventory**: `inventory/dns` → DNS server definitions  
- **Playbook**: `playbooks/provision_vm.yml` → VM provisioning workflow  
- **Role**: `roles/nginx_setup/` → Configures Nginx reverse proxy  

---

## Naming Conventions
To ensure clarity and maintainability, the following conventions are applied:

- **Inventories**: lowercase, named after service/environment (`dns`, `jenkins`, `truenas`)  
- **Playbooks**: action + target (`provision_vm.yml`, `deploy_vscode_server.yml`)  
- **Roles**: service + `_setup` suffix (`nginx_setup`, `redis_setup`)  
- **Scripts**: snake_case (`create_linux_master_inventory.py`)  

Each role must include a `README.md` for documentation.

---

## Visual Diagram
Here’s a simplified view of the repository hierarchy:

```
ansible/
├── ansible.cfg          # Core configuration
├── all.yml              # Global variables
├── inventory/           # Service & environment inventories
│   ├── dns/             # DNS servers
│   ├── jenkins/         # Jenkins nodes
│   └── ...
├── playbooks/           # Automation workflows
│   ├── provision_vm.yml # VM provisioning
│   ├── nginx/           # Reverse proxy setup
│   └── ...
├── roles/               # Modular service setups
│   ├── nginx_setup/     # Nginx role
│   ├── docker_setup/    # Docker role
│   └── ...
└── filter_plugins/      # Custom Jinja2 filters
```

