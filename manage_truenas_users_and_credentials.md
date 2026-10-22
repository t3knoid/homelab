---
title: "Manage TrueNAS Users and Credentials"
---

# 👤 Manage TrueNAS Users and Credentials

Maintain existing local accounts, supplementary memberships, and credentials associated with [configure_truenas.yml](https://github.com/t3knoid/ansible/blob/main/playbooks/truenas/configure_truenas.yml). This does not manage Active Directory user lifecycles. See [Add TrueNAS Local Users](add_truenas_local_users.md) for initial creation.

## 📋 Prerequisites

- Identify account consumers, group memberships, numeric IDs, owned files, ACL references, scheduled tasks, and stored client credentials.
- Keep working administrator access and avoid changing the automation connection identity without a separate access migration plan.
- Review vault handling, password policy, and the intended distinction between password reset, access revocation, and account deletion.

## 📝 Procedure to Complete

1. Capture current non-secret account settings and approved desired memberships.
2. Document membership changes using the complete desired `groups` list rather than an append-only assumption.
3. Define a deliberate UI or validated middleware password-rotation workflow and update vault/consumers without exposing the secret.
4. Specify access revocation across SMB sessions, SSH keys, groups, application credentials, and other active consumers.
5. Treat account deletion and numeric-ID migration as separate approved operations with file-ownership review.

## 🔎 Ansible Integration

{% raw %}
```bash
ansible-playbook -i inventory/truenas/inventory.ini playbooks/truenas/configure_truenas.yml --limit truenas-01 --tags truenas_users --list-tasks --ask-vault-pass
```
{% endraw %}

This lists all configured groups/users plus preflight. Review [the defaults](https://github.com/t3knoid/ansible/blob/main/roles/truenas/defaults/main.yml) and [user tasks](https://github.com/t3knoid/ansible/blob/main/roles/truenas/tasks/users.yml): password and primary-group/UID settings are normally create-only. Changing vault alone does not rotate an existing password. The role resends a configured password when `smb` changes; validate that transition deliberately.

Removing an account from the list does not delete it. `state: absent` is destructive, and `delete_group` defaults to true. `password_disabled: true` is not compatible with `smb: true` and must not be presented as a universal SMB revocation mechanism.

## ✅ Verification and Recovery

- Test intended access and denied access with fresh client sessions; verify shared services and automation still authenticate.
- Confirm vault and consumer credentials reflect the approved final state without logging secrets.
- Document a controlled reset/recovery process. Previous passwords cannot be read back from TrueNAS, and deleting/recreating a user is not a safe password rollback.

