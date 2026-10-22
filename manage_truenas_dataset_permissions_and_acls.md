---
title: "Manage TrueNAS Dataset Permissions and ACLs"
---

# 🔐 Manage TrueNAS Dataset Permissions and ACLs

Define ownership, POSIX permissions, SMB ACLs, and multiprotocol access for datasets managed through [configure_truenas.yml](https://github.com/t3knoid/ansible/blob/main/playbooks/truenas/configure_truenas.yml). Creating a user or share does not grant dataset access. See [Add TrueNAS Local Users](add_truenas_local_users.md) and [Add TrueNAS Shares](add_truenas_shares.md).

## 📋 Prerequisites

- Record the dataset path, permission model, owner/group IDs, client protocols, and allowed/denied operations.
- Capture the existing ACL, ownership, inheritance settings, and approved recovery method; verify backups before changing existing data.
- Resolve local or directory-service identities before applying permissions. Keep administrative access available.

## 📝 Procedure to Complete

1. Document how to inspect current permissions in the installed TrueNAS release without modifying them.
2. Define separate POSIX, SMB ACL, and multiprotocol decision paths, including inheritance and share-level access controls.
3. Specify the approved UI workflow or exact middleware method and payload for each supported model.
4. Test on a new dataset before exposing its shares; explicitly approve any recursive change to existing data.
5. Reconcile approved automation with host variables and document the recovery sequence.

## 🔎 Ansible Integration

Review [role defaults](https://github.com/t3knoid/ansible/blob/main/roles/truenas/defaults/main.yml) and [share tasks](https://github.com/t3knoid/ansible/blob/main/roles/truenas/tasks/shares.yml). `truenas_post_calls` supports raw operations, but these run after shares/resources, are not generally idempotent, and do not establish a pre-exposure permissions gate. Do not provide a generic recursive `chmod` or ACL-reset command as a substitute for a tested policy.

{% raw %}
```bash
ansible-playbook -i inventory/truenas/inventory.ini playbooks/truenas/configure_truenas.yml --limit truenas-01 --tags truenas_shares --list-tasks --ask-vault-pass
```
{% endraw %}

This command lists scope only. The tag covers every configured SMB/NFS share, additional resource, and post-call, not just permissions.

## ✅ Verification and Recovery

- Test intended access and denied access using non-administrator identities; verify UID/GID and inheritance from each client protocol.
- Confirm existing shares and administrative access remain functional.
- Complete the ACL/ownership restore procedure and distinguish metadata recovery from restoring file contents. A dataset snapshot rollback may discard subsequent writes and is not a routine permissions undo operation.

