---
title: "Update TrueNAS Safely"
---

# 🔄 Update TrueNAS Safely

Use the optional update stage in [configure_truenas.yml](https://github.com/t3knoid/ansible/blob/main/playbooks/truenas/configure_truenas.yml) to install an approved TrueNAS release, optionally reboot, and verify service health. This is not an unattended update policy.

## 📋 Prerequisites

- Approve the target release/train after reviewing release notes, hardware compatibility, application dependencies, and support constraints.
- Schedule an outage window and coordinate SMB/NFS clients, backup jobs, and other consumers.
- Export a usable configuration backup, handle any secret seed/encryption recovery material securely, and verify independent data backups.
- Confirm pool health, free space, local administrator/console access, and a documented boot recovery path.

## 📝 Procedure to Complete

1. Record the current release, boot environments, health baseline, and selected update target.
2. Set reviewed `truenas_update_enabled`, optional `truenas_update_train`/`truenas_update_version`, and an explicit reboot policy.
3. Document pre-update draining, installation, approved reboot, and expected middleware readiness checks.
4. Validate share access, directory integration, applications, monitoring, and backup operations after boot.
5. Restore the routine inventory update flags to the approved steady-state policy.

## 🔎 Ansible Integration

{% raw %}
```bash
ansible-playbook -i inventory/truenas/inventory.ini playbooks/truenas/configure_truenas.yml --limit truenas-01 --tags truenas_update --list-tasks --ask-vault-pass
```
{% endraw %}

This lists tasks only. The stage defaults to disabled; selecting its tag does not override `truenas_update_enabled: false`. [Update tasks](https://github.com/t3knoid/ansible/blob/main/roles/truenas/tasks/update.yml) call `update.run` with reboot disabled, then reboot separately only when the update reports changed and `truenas_update_reboot` is true. Without a pinned target, empty train/version inputs do not express an approved release. Check mode does not install or establish update compatibility.

## ✅ Verification and Recovery

- Verify the running release after any reboot, middleware readiness, pool health, protocol services, and client access.
- Document boot-environment recovery and configuration restoration for the supported release; account for any post-update data changes.
- Do not upgrade pool feature flags during initial verification or assume an older boot environment can use a pool after an irreversible feature upgrade.

