---
title: "️ Troubleshoot TrueNAS Configuration Runs"
---

# 🛠️ Troubleshoot TrueNAS Configuration Runs

Diagnose failures in [configure_truenas.yml](https://github.com/t3knoid/ansible/blob/main/playbooks/truenas/configure_truenas.yml) without blindly rerunning every stage. Refer to [Bootstrap TrueNAS for Ansible](bootstrap_truenas_for_ansible.md), [Add TrueNAS Local Users](add_truenas_local_users.md), and [Add TrueNAS Shares](add_truenas_shares.md) for prerequisites.

## 📋 Evidence to Collect

- Record the selected inventory/hostname, tags, check-mode flag, role stage, non-secret error text, and time of failure.
- Determine which earlier tasks succeeded; a failed play does not roll back completed API operations.
- Keep passwords, session material, decrypted inventory, and secret-bearing verbose logs out of tickets. Preserve `truenas_no_log: true` by default.

## 🔎 Initial Controller Checks

{% raw %}
```bash
ansible-inventory -i inventory/truenas/inventory.ini --graph
ansible-playbook -i inventory/truenas/inventory.ini playbooks/truenas/configure_truenas.yml --limit truenas-01 --syntax-check --ask-vault-pass
ansible-playbook -i inventory/truenas/inventory.ini playbooks/truenas/configure_truenas.yml --limit truenas-01 --tags truenas_preflight --ask-vault-pass
```
{% endraw %}

Preflight connects to the NAS for read-only readiness, version, and administrator checks. Syntax validation alone does not establish SSH, root escalation, middleware access, or API compatibility. Use `-k`/`-K` only for the corresponding connection/become password, separately from vault authentication.

## 📝 Symptom Matrix to Complete

| Symptom                                     | First Boundary to Check                               | Required Guidance                                                |
| ------------------------------------------- | ----------------------------------------------------- | ---------------------------------------------------------------- |
| SSH or become failure                       | Inventory connection identity and approved privileges | Verified connection/host-key checks and console recovery         |
| Middleware not ready or unsupported version | Always-run preflight                                  | Expected wait behavior and supported-release decision            |
| Group name not found during preview         | Existing NAS identities versus simulated creation     | Staged prerequisite creation, not ignored API errors             |
| Share path missing during preview           | Dataset existence and selected tags                   | Dataset creation before share validation                         |
| Existing password unchanged                 | Create-only secret handling                           | Deliberate password reset, not vault-only edits                  |
| Permission denied from a client             | Dataset ACL, share restrictions, identity mapping     | Non-administrator access tests without globally loosening access |
| Repeated changes or unexpected side effects | Selected complete lists and raw post-calls            | Review non-idempotent calls and completed stages before retry    |

## ✅ Recovery and Escalation

- Inspect actual NAS state after partial failure, repair the specific dependency, and retry only the reviewed stage.
- Do not bypass version checks, remove identity/state safeguards, or rerun mutating raw post-calls merely to obtain a successful recap.
- Define escalation criteria for storage health issues, unknown API/schema failures, lost administrator access, and suspected exposure of credentials or data.
