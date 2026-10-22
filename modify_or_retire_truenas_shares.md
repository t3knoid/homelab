---
title: "Modify or Retire TrueNAS Shares"
---

# 📁 Modify or Retire TrueNAS Shares

Change or retire SMB/NFS exports using [configure_truenas.yml](https://github.com/t3knoid/ansible/blob/main/playbooks/truenas/configure_truenas.yml) while preserving datasets and retained data. Use [Add TrueNAS Shares](add_truenas_shares.md) for new exports and [Manage TrueNAS Dataset Permissions and ACLs](manage_truenas_dataset_permissions_and_acls.md) for access-policy changes.

## 📋 Prerequisites

- Identify the exact share, dataset path, consumers, active sessions/mounts, backup policy, and approved maintenance window.
- Capture current share settings and inventory definitions, including client restrictions and identity mappings.
- Confirm whether a rename, replacement export, access restriction, or deletion is actually required.

## 📝 Procedure to Complete

1. Notify owners and drain SMB sessions or unmount NFS clients safely, accounting for in-flight writes.
2. Define the migration path and client-side changes before changing the export.
3. Review the entire selected inventory stage and document the exact desired-state change.
4. Preview, approve, and apply only the intended share change using the existing playbook.
5. Verify unrelated exports and update client/deployment definitions to prevent accidental recreation.

## 🔎 Ansible Integration

SMB lookup uses `name`; NFS lookup uses `path`. Changing a lookup key can create another export while leaving the old export present. Omitting an entry does not delete it; explicit `state: absent` does. Dataset deletion is not supported by this role and is not part of share retirement.

{% raw %}
```bash
ansible-playbook -i inventory/truenas/inventory.ini playbooks/truenas/configure_truenas.yml --limit truenas-01 --tags truenas_shares --list-tasks --ask-vault-pass
```
{% endraw %}

This lists scope only. Before adding apply commands, account for all SMB/NFS definitions, `truenas_resources`, and non-idempotent `truenas_post_calls` selected by this tag. Do not stop a protocol service shared by other exports.

## ✅ Verification and Recovery

- Verify the old export is absent or restricted as intended and the replacement works for authorized clients.
- Confirm retained datasets/data and unrelated shares remain intact.
- Document how to restore the prior share definition and reconnect clients; restoring an export does not reverse data writes or permission changes.
