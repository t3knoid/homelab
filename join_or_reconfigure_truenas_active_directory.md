---
title: "Join or Reconfigure TrueNAS Active Directory"
---

# 🌐 Join or Reconfigure TrueNAS Active Directory

Manage NAS network configuration and AD integration through [configure_truenas.yml](https://github.com/t3knoid/ansible/blob/main/playbooks/truenas/configure_truenas.yml). This does not create domain users or replace domain-controller administration. See [the contributor guide](../contrib/truenas-role-contributor-guide.md) for the role's API mapping.

## 📋 Prerequisites

- Confirm domain DNS resolution, time synchronization, domain-controller reachability, unique NAS identity, and approved directory join permissions.
- Record current network/AD settings, share dependencies, identity mappings, and an approved maintenance window.
- Keep a local administrator and console access available independently of AD. Store join credentials in the encrypted host vault.

## 📝 Procedure to Complete

1. Document release-appropriate DNS/time/connectivity checks and accepted results before joining.
2. Review `truenas_network_configuration` and `truenas_ad` in host variables, including the correct domain and NAS hostname.
3. Define how to preview supported configuration differences without assuming a dry run can validate a complete domain join.
4. Add approved join/reconfiguration commands and expected middleware job results after testing.
5. Verify directory identities and SMB access, then reconcile any temporary credentials and permissions.

## 🔎 Ansible Integration

{% raw %}
```bash
ansible-playbook -i inventory/truenas/inventory.ini playbooks/truenas/configure_truenas.yml --limit truenas-01 --tags truenas_ad --list-tasks --ask-vault-pass
```
{% endraw %}

The tag includes both network settings and AD configuration after preflight. Changing DNS or directory settings can disrupt access; it is not an AD-only credential test. Review [directory-service tasks](https://github.com/t3knoid/ansible/blob/main/roles/truenas/tasks/directory_services.yml) and keep `truenas_no_log: true`. Join credentials are sent when the managed AD configuration changes; replacing a vault value alone is not proof of a successful rejoin.

## ✅ Verification and Recovery

- Verify domain resolution, directory-service health, expected users/groups, and authenticated SMB access using fresh sessions.
- Confirm local administrative access and existing share permissions remain usable.
- Document recovery for a failed join and network change separately. Do not assume restoring old inventory text automatically reverses domain membership or machine-account changes.

