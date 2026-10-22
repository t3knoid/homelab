---
title: "Add TrueNAS Shares"
---

# 📁 Add TrueNAS Shares

Use [configure_truenas.yml](https://github.com/t3knoid/ansible/blob/main/playbooks/truenas/configure_truenas.yml) to create datasets and SMB or NFS shares on an existing TrueNAS 25.10+ system. This procedure targets `truenas-01` using [its inventory](https://github.com/t3knoid/ansible/blob/main/inventory/truenas/inventory.ini). It does not create a storage pool, migrate existing data, or grant access merely by exporting a path.

## 📋 Prerequisites

- Run commands from the repository root with the repository's Ansible environment active and vault credentials available.
- Complete initial administrator setup in the TrueNAS UI. The inventory SSH user, currently `ansible`, must be able to connect and become root. The role calls middleware locally over SSH, not with a web UI password or HTTP API key.
- Verify the parent pool exists and is healthy, has enough capacity, and has an appropriate backup/snapshot policy. Confirm that new paths do not overlap existing exports unintentionally.
- Decide the protocol, dataset path, SMB share name, allowed NFS clients, identity mapping, and ACL/POSIX policy. Use separate datasets when workloads require incompatible permissions.
- Create required users/groups first with [Add TrueNAS Local Users](add_truenas_local_users.md), or verify directory-service identities already resolve. The examples use an existing `projectuser` account and `project_access` group.
- Review [the role defaults](https://github.com/t3knoid/ansible/blob/main/roles/truenas/defaults/main.yml) and [TrueNAS Role Contributor Guide](truenas_role_contributor_guide.md). The examples below intentionally export one dataset over both SMB and NFS; omit the unused protocol for a single-protocol share.

## 📝 1. Add Dataset and Share Definitions

Edit [the NAS host variables](https://github.com/t3knoid/ansible/blob/main/inventory/truenas/host_vars/truenas-01/default.yml). Append to the existing lists rather than replacing them or adding duplicate top-level YAML keys. The snippets show only the entries to add. Keep each list defined in one host-variable file so later files do not override the entire list unexpectedly.

{% raw %}
```yaml
truenas_datasets:
  - name: Data/projects
    share_type: MULTIPROTOCOL
    compression: LZ4

truenas_smb_shares:
  - name: projects
    path: /mnt/Data/projects
    purpose: MULTIPROTOCOL_SHARE
    comment: Project files
    options:
      purpose: MULTIPROTOCOL_SHARE

truenas_nfs_shares:
  - path: /mnt/Data/projects
    networks: ["192.168.20.0/24"]
    ro: false
    mapall_user: projectuser
    mapall_group: project_access
```
{% endraw %}

Replace the pool, dataset, subnet, and identities for the intended deployment. NFS `mapall_*` maps every client request to the selected local identity; use it only when that shared-identity access model is intended. Do not combine `mapall_*` and `maproot_*`. Do not copy an unrestricted `networks: []` or a privileged root mapping from another share without reviewing exposure and server policy.

For SMB-only use `share_type: SMB` and `purpose: DEFAULT_SHARE`, with the same value in `options.purpose`, and omit the NFS entry. For NFS-only, omit the SMB entry and choose dataset creation properties supported by the installed TrueNAS release and your permissions policy. The role passes dataset properties to middleware; it does not translate arbitrary share-type names or convert an existing dataset's create-only preset.

Enable the needed services by adding or updating entries in the existing `truenas_services` list:

{% raw %}
```yaml
truenas_services:
  - name: cifs
    enable: true
    state: started
  - name: nfs
    enable: true
    state: started
```
{% endraw %}

Keep only the protocols you intend to serve, preserving unrelated service entries. Starting a service can expose other already-configured shares; review them and the network firewall policy before enabling it.

## 🔎 2. Validate the Change and Task Scope

{% raw %}
```bash
ansible-inventory -i inventory/truenas/inventory.ini --graph
ansible-playbook -i inventory/truenas/inventory.ini playbooks/truenas/configure_truenas.yml --limit truenas-01 --syntax-check --ask-vault-pass
ansible-playbook -i inventory/truenas/inventory.ini playbooks/truenas/configure_truenas.yml --limit truenas-01 --tags truenas_datasets,truenas_shares,truenas_services --list-tasks --ask-vault-pass
```
{% endraw %}

Preflight always checks middleware readiness, version, and initial administrator setup. Each selected stage processes its complete configured list, not only the new entry. In particular, `truenas_shares` includes all SMB/NFS definitions, `truenas_resources`, and non-idempotent `truenas_post_calls`. Review all those inputs, especially permission-changing calls and any `state: absent`, before using that tag. User/group creation, network/AD configuration, administrator changes, and updates are not selected by these tags.

Add `-k` if the inventory connection user needs an SSH password and `-K` if becoming root needs a separate password. These are different from `--ask-vault-pass`; omit prompts already handled by your configured credentials. Keep `truenas_no_log: true` and do not publish decrypted inventory or secret-bearing diffs.

## 💾 3. Create the Dataset Before Exposing It

Preview then apply the dataset stage:

{% raw %}
```bash
ansible-playbook -i inventory/truenas/inventory.ini playbooks/truenas/configure_truenas.yml --limit truenas-01 --tags truenas_datasets --check --ask-vault-pass
ansible-playbook -i inventory/truenas/inventory.ini playbooks/truenas/configure_truenas.yml --limit truenas-01 --tags truenas_datasets --ask-vault-pass
```
{% endraw %}

Confirm `Data/projects` exists at `/mnt/Data/projects`. Dataset creation and share creation are separate operations. A combined first-run `--check` does not create the path, so subsequent share validation may reject a nonexistent path. Complete dataset creation before previewing new shares.

In the TrueNAS UI, configure the new dataset's ownership and ACL or POSIX permissions for the approved users/groups before exposing it. Verify both authorized and unauthorized identities. Do not assume the share definition or dataset preset grants the required access; do not recursively reset permissions on existing data as a routine addition step.

The role can automate approved permission operations through `truenas_post_calls` such as `filesystem.setperm` or a release-appropriate ACL method, but those calls run after share creation and are not generally idempotent. They are not a safe substitute for the pre-exposure permissions review. Check existing post-calls for anything that would overwrite the policy you just set. An SMB/NFS multiprotocol dataset needs a permissions design compatible with both client identity models.

## ▶️ 4. Preview and Apply Shares and Services

With dataset paths and identities present, preview the selected stages:

{% raw %}
```bash
ansible-playbook -i inventory/truenas/inventory.ini playbooks/truenas/configure_truenas.yml --limit truenas-01 --tags truenas_shares,truenas_services --check --ask-vault-pass
```
{% endraw %}

Review the reported changes. Check mode does not execute mutating raw API calls or prove that client access will work. Once approved, apply:

{% raw %}
```bash
ansible-playbook -i inventory/truenas/inventory.ini playbooks/truenas/configure_truenas.yml --limit truenas-01 --tags truenas_shares,truenas_services --ask-vault-pass
```
{% endraw %}

Shares/resources are configured first; service autostart and running state are managed last. Do not use the entire untagged playbook for a routine share addition unless you have reviewed all configured stages, including network/AD, accounts, updates, and raw middleware calls.

## ✅ 5. Verify From Clients

- In the TrueNAS UI, confirm the dataset, SMB share name/path/purpose, NFS client restrictions/mapping, and service state/autostart settings.
- From an SMB client, connect to `\\truenas-01\projects` using a permitted user's credentials. Use a hostname/FQDN that resolves in the client network. Test the approved read/write/delete operations and verify an unauthorized account is denied.
- From an authorized NFS client, mount `truenas-01:/mnt/Data/projects` at an existing temporary mount point using the site's supported NFS version and mount options. Confirm the effective UID/GID and the expected read/write behavior; also verify restrictions from an unapproved client. Unmount the temporary test mount afterward.
- For multiprotocol access, create a disposable file from each protocol and verify ownership and access through the other. Do not use production data for destructive permission tests.
- Check that existing shares still work. Rerun the tagged preview to investigate unexpected drift; configured raw post-calls may continue to report changes because they are not idempotent.

## 🛠️ Recovery and Changes to Existing Shares

If creation fails, verify the path, dataset creation properties, local/directory identities, SMB purpose, and mutually exclusive NFS mapping fields before retrying. Do not bypass the version check or loosen permissions globally to clear an error.

SMB lookup uses `name`; NFS lookup uses `path`. Renaming those fields can create a new share and leave the old one present. Removing a definition from inventory does not delete the existing share. Review any rename/removal as a separate change; an explicit share entry with `state: absent` deletes that share and can interrupt connected clients.

For an approved rollback, remove or disable only the new export using the UI or an explicit reviewed `state: absent` definition, then reconcile inventory so a later run cannot recreate it. Do not stop a protocol service used by other shares. The role does not delete datasets; retain the dataset and any written data until a separate retention/deletion decision is approved.
