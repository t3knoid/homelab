---
title: "Add TrueNAS Local Users"
---

# 👤 Add TrueNAS Local Users

Use [configure_truenas.yml](https://github.com/t3knoid/ansible/blob/main/playbooks/truenas/configure_truenas.yml) to add local users and groups to an existing TrueNAS 25.10+ system. This procedure targets `truenas-01` using [its inventory](https://github.com/t3knoid/ansible/blob/main/inventory/truenas/inventory.ini). It does not create Active Directory users or grant dataset access automatically. For share access, continue with [Add TrueNAS Shares](add_truenas_shares.md).

## 📋 Prerequisites

- Run commands from the repository root with the repository's Ansible environment active and vault credentials available.
- Complete initial administrator setup in the TrueNAS UI. Enable SSH for the inventory connection user, currently `ansible`, and verify that it can become root. The role uses local middleware over SSH, not a web UI password or an HTTP API key.
- Keep an existing administrator session available. Do not change the Ansible connection account or remove its privilege while adding another user.
- Choose an unused username, UID, group name, and GID. Check existing local and directory-service identities in TrueNAS; coordinate numeric IDs with NFS clients where identity mapping depends on them.
- Review [the role defaults](https://github.com/t3knoid/ansible/blob/main/roles/truenas/defaults/main.yml) and [TrueNAS Role Contributor Guide](truenas_role_contributor_guide.md) for supported fields. The IDs and names below are examples, not reserved assignments.

## 📝 1. Add Group and User Definitions

Edit [the NAS host variables](https://github.com/t3knoid/ansible/blob/main/inventory/truenas/host_vars/truenas-01/default.yml). Append entries to the existing lists; do not replace existing accounts or define the same top-level YAML key twice. Keep each variable in one host-variable file so a later file cannot override the complete list unexpectedly.

{% raw %}
```yaml
truenas_groups:
  - name: project_access
    gid: 3100

truenas_users:
  - username: projectuser
    uid: 3100
    full_name: Project Share User
    password: "{{ vault_projectuser_password }}"
    password_disabled: false
    smb: true
    group_create: false
    group: project_access
    groups: [project_access]
    shell: /usr/sbin/nologin
    ssh_password_enabled: false
    home: /var/empty
```
{% endraw %}

This example creates an SMB account without interactive SSH access. `group` is the primary group name because `group_create` is false. `groups` is the complete desired supplementary membership list, not an append operation; include every intended supplementary group when editing an existing user. Do not add builtin groups such as `users` without checking TrueNAS restrictions, or grant administrator/sudo privileges merely to access a share.

For a non-SMB service account, use `smb: false` and choose an appropriate password policy. `password_disabled: true` cannot be combined with `smb: true`. For an interactive account, choose a shell returned by `user.shell_choices`, a valid home path, and an explicit SSH authentication policy. `home_create: true` only creates a home when the account is first created; its parent dataset must already exist. A user-only tagged run does not create datasets.

## 🔐 2. Store the Password in Vault

Add `vault_projectuser_password` to the encrypted host vault at `inventory/truenas/host_vars/truenas-01/vault.yml` using the existing vault workflow:

{% raw %}
```bash
ansible-vault edit inventory/truenas/host_vars/truenas-01/vault.yml
```
{% endraw %}

Set the secret in that encrypted file, not in a command-line extra variable, shell history, or the unencrypted user definition. If this host has no vault file yet, use `ansible-vault create` at the same path instead. Follow the repository's vault identity/password-file setup, or supply the usual vault password prompt. Keep `truenas_no_log: true`; do not publish decrypted inventory output or diagnostic logs containing passwords.

## 🔎 3. Validate and Preview

{% raw %}
```bash
ansible-inventory -i inventory/truenas/inventory.ini --graph
ansible-playbook -i inventory/truenas/inventory.ini playbooks/truenas/configure_truenas.yml --limit truenas-01 --syntax-check --ask-vault-pass
ansible-playbook -i inventory/truenas/inventory.ini playbooks/truenas/configure_truenas.yml --limit truenas-01 --tags truenas_users --list-tasks --ask-vault-pass
```
{% endraw %}

The `truenas_users` tag includes both groups and users, plus the always-tagged preflight. It processes all configured entries in those lists, including existing users and any `state: absent` entries; it does not select just the new username. It skips updates, administrator settings, network/AD, datasets, shares, and services. Inspect the lists and task selection before applying.

If the user's group already exists on the NAS, preview both stages together:

{% raw %}
```bash
ansible-playbook -i inventory/truenas/inventory.ini playbooks/truenas/configure_truenas.yml --limit truenas-01 --tags truenas_users --check --ask-vault-pass
```
{% endraw %}

If the group is new, first preview and then apply only groups, after reviewing all `truenas_groups` entries:

{% raw %}
```bash
ansible-playbook -i inventory/truenas/inventory.ini playbooks/truenas/configure_truenas.yml --limit truenas-01 --tags truenas_groups --check --ask-vault-pass
ansible-playbook -i inventory/truenas/inventory.ini playbooks/truenas/configure_truenas.yml --limit truenas-01 --tags truenas_groups --ask-vault-pass
ansible-playbook -i inventory/truenas/inventory.ini playbooks/truenas/configure_truenas.yml --limit truenas-01 --tags truenas_users --check --ask-vault-pass
```
{% endraw %}

Check mode does not actually create groups, so a combined first-run preview may fail when users resolve a new group name to an ID. That is a dependency limitation, not permission to ignore unrelated errors. Previews still connect to the NAS and run read-only preflight checks; user results are deliberately hidden by `no_log`.

Add `-k` if the SSH connection account requires a password. Add `-K` if sudo requires a separate password. These prompts are distinct from `--ask-vault-pass`; omit prompts already handled by your configured credentials.

## ▶️ 4. Apply Users

{% raw %}
```bash
ansible-playbook -i inventory/truenas/inventory.ini playbooks/truenas/configure_truenas.yml --limit truenas-01 --tags truenas_users --ask-vault-pass
```
{% endraw %}

Groups are processed before users. Do not run the entire untagged playbook for a routine user addition unless you have reviewed every other configured stage, including updates, AD, and raw middleware calls.

## ✅ 5. Verify Access

- In the TrueNAS UI, verify the username, UID, primary/supplementary groups, SMB authentication setting, shell, and SSH policy.
- Grant the intended dataset ACL or POSIX permissions using the approved storage policy. Creating the user or adding it to a local group does not by itself grant filesystem access or bypass an SMB share ACL.
- Test SMB access from a client with the new account, including an allowed operation and an operation it should not be allowed to perform. Close existing sessions or cached credentials before retesting changed memberships.
- Confirm the account cannot log in over SSH if it is intended to be share-only. Confirm the administrator and Ansible connection accounts still work.
- Rerun the tagged `--check` command after successful creation to review unexpected drift. Non-secret managed settings should converge; check mode cannot verify a password by reading it back.

## 🛠️ Password Changes and Recovery

Changing the vault value alone does not rotate an existing user's password. Password, UID, primary group, `group_create`, and home-creation settings are normally create-only in this role. When the `smb` flag changes, the role resends the configured password because TrueNAS requires it; retain a usable vault value for that transition. Use an approved explicit `user.set_password` workflow or the TrueNAS UI for an intentional password reset, then update vault to match.

For failed creation, inspect the account and group in the UI before retrying. Correct duplicate IDs, missing group names, password policy, or home-path prerequisites rather than disabling safety checks or logging passwords. Do not delete and recreate a live account merely to change a create-only setting: ownership and ACL references depend on numeric IDs.

Removing an item from `truenas_users` does not delete the account. Explicit `state: absent` does, and `delete_group` defaults to true. Treat rollback deletion as a separate approved change, check data ownership and group sharing first, and use `delete_group: false` when the primary group must remain. No account deletion is part of this add-user procedure.
