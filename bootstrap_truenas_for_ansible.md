---
title: "Bootstrap TrueNAS for Ansible"
---

# 🚀 Bootstrap TrueNAS for Ansible

Prepare an already-installed TrueNAS 25.10+ system for [configure_truenas.yml](https://github.com/t3knoid/ansible/blob/main/playbooks/truenas/configure_truenas.yml). This is not an operating-system installation or storage-pool provisioning procedure. See the [TrueNAS Role Contributor Guide](truenas_role_contributor_guide.md).

## 📋 Prerequisites

- Record the NAS address, supported version, DNS/time requirements, administrator recovery access, and approved SSH source networks.
- Complete initial local administrator setup in the UI; the role requires this before configuration.
- Prepare the controller's repository Ansible environment and vault access. Never store plaintext credentials in inventory or command history.

## 📝 Procedure to Complete

1. Document how to enable SSH and create or prepare the inventory connection account using the installed TrueNAS UI.
2. Install and verify the controller's public key and the NAS host-key fingerprint through a trusted channel.
3. Grant only the approved privilege needed to become root for local middleware access, without locking out the current administrator.
4. Update [the inventory](https://github.com/t3knoid/ansible/blob/main/inventory/truenas/inventory.ini) and host variables, preserving the existing naming and encrypted secret conventions.
5. Validate preflight before selecting individual configuration stages; do not immediately run all configured stages.

## 🔎 Initial Validation

Run from the repository root after connection preparation:

{% raw %}
```bash
ansible-inventory -i inventory/truenas/inventory.ini --graph
ansible-playbook -i inventory/truenas/inventory.ini playbooks/truenas/configure_truenas.yml --limit truenas-01 --syntax-check --ask-vault-pass
ansible-playbook -i inventory/truenas/inventory.ini playbooks/truenas/configure_truenas.yml --limit truenas-01 --tags truenas_preflight --ask-vault-pass
```
{% endraw %}

The final command connects to the NAS and performs read-only readiness, version, and administrator checks. Add `-k` for an SSH password or `-K` for a become password when required; neither is the vault password. The role uses local middleware over SSH, not a web UI password or HTTP API key.

## ✅ Verification and Recovery

- Verify key-based SSH, approved root escalation, successful preflight, and a separate working administrator session.
- Document how to recover access from the console if SSH, keys, sudo, or network settings are wrong.
- Continue with [Add Local Users](truenas_add_users.md) and [Add Shares](truenas_add_shares.md) using targeted tags.

