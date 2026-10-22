---
title: "Create and Modify TrueNAS Datasets"
---

# 💾 Create and Modify TrueNAS Datasets

Manage filesystem datasets through `truenas_datasets` and [configure_truenas.yml](https://github.com/t3knoid/ansible/blob/main/playbooks/truenas/configure_truenas.yml). Pool creation, dataset deletion, data migration, and block-storage provisioning are outside this procedure. See [Add TrueNAS Local Users](add_truenas_local_users.md) and [Manage TrueNAS Dataset Permissions and ACLs](manage_truenas_dataset_permissions_and_acls.md) for exposure and access.

## 📋 Prerequisites

- Verify the parent pool/dataset, available capacity, health, backups, and approved dataset naming.
- Decide the workload, share protocol, permissions model, quota policy, compression, and encryption requirements before creation.
- Capture current properties and consumer dependencies before editing an existing dataset.

## 📝 Procedure to Complete

1. Add reviewed examples for an empty filesystem dataset and a child dataset, preserving existing `truenas_datasets` entries.
2. Distinguish mutable properties from `truenas_dataset_create_only_keys` in [the defaults](https://github.com/t3knoid/ansible/blob/main/roles/truenas/defaults/main.yml).
3. Preview and apply only the dataset stage after confirming parent dependencies.
4. Establish permissions and backup policy before exposing the path to clients.
5. Define a migration procedure rather than suggesting in-place changes to creation-only encryption, type, or share-preset fields.

## 🔎 Ansible Integration

{% raw %}
```bash
ansible-playbook -i inventory/truenas/inventory.ini playbooks/truenas/configure_truenas.yml --limit truenas-01 --tags truenas_datasets --list-tasks --ask-vault-pass
```
{% endraw %}

This lists preflight and all configured datasets. [Dataset tasks](https://github.com/t3knoid/ansible/blob/main/roles/truenas/tasks/datasets.yml) create or adjust filesystem datasets but never delete them. The tag does not create users, shares, or services, and check mode does not create paths for later share validation. Omitting or renaming a dataset definition does not migrate or remove existing data.

## ✅ Verification and Recovery

- Verify the dataset identity, mount path, properties, space limits, and intended permissions in TrueNAS.
- Confirm existing consumers and backup policies still work; use disposable test files for access checks.
- Document property rollback separately from data migration recovery. Do not destroy a newly created dataset containing data merely to correct a creation-only property.
