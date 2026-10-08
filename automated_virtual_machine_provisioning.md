---
title: "️ Automated Virtual Machine Provisioning"
---

# 🖥️ Automated Virtual Machine Provisioning

This homelab supports two workflows for creating virtual machines on Proxmox:

- **Ansible-only provisioning**
- **Terraform + Ansible provisioning**

Both workflows clone an existing cloud-init template and share Ansible tasks for startup, cloud-init verification, SSH trust bootstrap, and recoverable finalization. They are **creation workflows**, not general-purpose hardware-update playbooks. Not every inventory setting is implemented identically in both backends.

> ❗ **IMPORTANT: Virtual Machine Templates**
> The template selected by `global_os[vms_os].template` must already exist in the Proxmox cluster.
> 👉 See **[Proxmox VM Template Runbook](proxmox_vm_template_runbook.md)**.

---

## 🔧 Provisioning Modes

| Mode                    | VM Creation                                                                                                                           | Subsequent Lifecycle                                                                                                                           |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| **Ansible-only**        | Proxmox API modules clone the template, resize the boot disk when requested, apply hardware/network settings, and add optional disks. | Ansible manages migration, startup, cloud-init verification, and finalization.                                                                 |
| **Terraform + Ansible** | Terraform creates the clone and defines its initial hardware, disks, NIC, and cloud-init references.                                  | Ansible manages migration, startup, cloud-init verification, and finalization. Terraform state records ownership and is used for safe removal. |

### Terraform Is Creation-Only

The current Terraform resource ignores later changes to `target_node`, `vm_state`, `disk`, and `cicustom`. This prevents a rerun from reversing Ansible's migration, power-state changes, or cloud-init-drive removal.

Completed VMs skip the creation stage **after ownership validation**. Changing inventory hardware settings does not reconcile an already completed guest. Use a separately reviewed maintenance workflow for hardware updates.

---

## 🧭 High-Level Workflow

{% raw %}
```text
[Acquire per-VM workflow lock]
        |
        v
[Discover VM and pending finalization checkpoint]
        |
        v
[Validate Terraform ownership when enabled]
        |
        v
<Creation or initialization needed?>
  |
  +-- Yes --> [Update DNS and render user-data/network-data]
  |                              |
  |                              v
  |           [Clone and configure using selected backend]
  |                              |
  |                              v
  |           [Migrate to requested node when necessary]
  |                              |
  |                              v
  |           [Start guest and verify its connection]
  |                              |
  |                              v
  |           [Poll and verify structured cloud-init status]
  |                              |
  |                              v
  |           [Update known_hosts] --> [FINALIZE below]
  |
  +-- No --> <Pending finalization?>
           |
           +-- Yes --> [Start and verify existing guest]
           |           [No clone or Terraform apply]
           |                         |
           |                         v
           |                  [FINALIZE below]
           |
           +-- No --> [Skip completed creation stage]
                       |
                       v
                     [FINISH below]

FINALIZE
[Write pending-finalization checkpoint]
        |
        v
[Remove detected cloud-init drive]
        |
        v
[Reboot guest; verify changed boot ID and connection]
        |
        v
[Clear checkpoint] --> [FINISH]

FINISH
[Release workflow lock]
        |
        v
[Continue post-provision stages when using full wrapper]
```
{% endraw %}

Failures stop the workflow. Normal failure cleanup releases the lock; Terraform cleanup removes the current attempt's saved plan and restricts state-file permissions. Cloud-init failures do not automatically trigger a reboot or mark initialization complete.

---

## 🧱 Shared Architecture

### Cloud-Init

Ansible renders **user-data and network-data** snippets in both modes. These configure the guest's management user, SSH keys, packages, timezone, network, and sudo settings. This VM workflow does not render a separate meta-data snippet.

Snippets are stored on the destination Proxmox node under `/var/lib/vz/snippets` and referenced through `local:snippets/...`. Ensure that storage supports snippets and that the configured node, bridge, subnet, gateway, and DNS are correct.

The current network template uses `ens18` and a `/24` prefix. Do not assume those defaults fit every template or network.

👉 See **[Cloud-Init](cloud-init.md)** for cloud-image background.

### Names and Networking

- `inventory_hostname` remains the managed-host identity for guest configuration and connectivity.
- `vms_name` is the canonical Proxmox VM name and defaults to the inventory hostname. Discovery, Terraform VM naming, and snippet filenames use it consistently.
- Structured NIC settings support `vms_config.nic0` and `vms_config.network.nic0`; the nested form takes precedence. Terraform normalizes these settings and preserves the VLAN tag.
- Confirm hostname resolution, SSH authentication, privilege escalation, and the intended guest interpreter. Startup uses `wait_for_connection`, which verifies Ansible connectivity and requires a usable guest Python interpreter; it is not merely a TCP-port test.

### Boot Sequencing

1. Start the guest and verify its connection, not the control node's connection.
2. Poll `cloud-init status --format=json` using a bounded command timeout and retry count.
3. Require successful exit status, `done` status, and no reported errors or degraded status.
4. Update `known_hosts` before finalization.
5. Record a pending-finalization checkpoint and remove the detected cloud-init drive.
6. Reboot through the guest and verify a changed boot ID and restored connection.
7. Clear the checkpoint only after that verification succeeds.

Cloud-init polling and the guest reboot action do not themselves require guest Python. The startup connection check does, as noted above.

### Bounded Cloud-Init Verification

| Variable                         | Default | Purpose                                  |
| -------------------------------- | ------- | ---------------------------------------- |
| `vms_cloud_init_poll_retries`    | `120`   | Retry bound for status polling.          |
| `vms_cloud_init_poll_delay`      | `15`    | Seconds between attempts.                |
| `vms_cloud_init_command_timeout` | `30`    | Maximum seconds for each status command. |

These are separate command and retry bounds, not a single exact wall-clock deadline. On failure, inspect `cloud-init status --long` and the guest's cloud-init logs before retrying. The workflow no longer reboots automatically merely because command output contains the word `error`.

---

## 🛡️ Terraform Safety Controls

### Ownership Before Side Effects

An existing VM must match `proxmox_vm_qemu.vm` in Terraform state by canonical name and VMID. Validation occurs before DNS changes, before skipping a completed guest, and again before planning.

Missing, unreadable, or mismatched ownership fails closed. A genuinely new guest without an existing module or state remains eligible for creation. Do not delete state to bypass a mismatch or import a guest without reviewing its identity and desired configuration.

### Saved-Plan Approval

Terraform plans are inspected as JSON before applying the **same unique saved-plan file**:

- Creation, updates, and no-op actions for the expected VM resource are allowed.
- Deletion alone and unrelated managed resources are rejected during provisioning.
- Replacement is rejected by default. After reviewing the affected VM and accepting loss of its existing data, explicitly set `vms_terraform_allow_replacement=true` to permit replacement.
- That replacement flag does not bypass ownership validation.

### Private Files and Diagnostics

Module directories use mode `0700`; generated configuration, saved plans, and state artifacts are protected with owner-only access. The Proxmox password remains in the generated input file but is declared sensitive in Terraform, and sensitive rendering/execution output is hidden from Ansible logs.

Failed plan/apply attempts save an owner-only `terraform-failure.log` in the host's Terraform module directory. Review it locally; it may contain secrets and must not be published. Apply may have partially changed the guest, so inspect state and Proxmox before retrying.

Saved-plan cleanup removes only the current attempt's plan. Keep Terraform state and its backups intact for recovery.

---

## 🔒 Concurrency and Recovery

### Per-VM Workflow Locks

Provisioning and removal acquire an atomic lock keyed by the Proxmox API endpoint and canonical VM name. The outer playbook lock covers discovery, DNS changes, creation/removal, and finalization. Nested Terraform role calls reuse the owning invocation's lock.

Competing workflows fail instead of overwriting configuration, applying another run's plan, or deleting another run's artifacts. Locks normally release in `always` cleanup. If the control-node process is killed, confirm no workflow is running before manually removing a stale lock.

`vms_terraform_lock_root` defaults to the Terraform root's `.workflow-locks` directory. These are **filesystem locks, not distributed locks**: use one control node, a shared lock location with reliable atomic directory creation, or external job serialization across control nodes.

### Finalization Checkpoints

Owner-only checkpoints under `vms_finalization_state_dir` identify the canonical VM name and VMID. The directory defaults to the Terraform root's `.finalization` directory.

If drive removal succeeded but final reboot failed, a rerun starts the existing guest and retries finalization without cloning or applying Terraform again. A mismatched checkpoint blocks the operation for review.

Legacy VMs created before checkpoints existed are considered complete when no cloud-init drive remains. Manually inspect any previously interrupted legacy VM before relying on that skip. Successful removal clears the removed VM's checkpoint.

---

## 🧬 Backend Differences

### Ansible-Only

Ansible uses `community.proxmox.proxmox_kvm` for cloning/configuration and `community.proxmox.proxmox_disk` for resizing and additional disks. Cloud-init references and hardware/network settings are applied through the VM configuration tasks.

### Terraform + Ansible

Terraform renders a per-host module and defines the clone's initial CPU, memory, boot disk, optional extra disk, NIC/VLAN, and cloud-init references. The VM is initially created stopped on the template's node. Ansible subsequently handles migration to the requested node, startup, cloud-init verification, and finalization.

Backend-specific limitations still apply. For example, the exposed serial-terminal setting is not currently honored as a conditional toggle by the Terraform resource, and raw `vms_config.net0` is not a Terraform input interface. Check the target backend's task/template implementation before assuming a setting is portable.

---

## 📦 Modules and Tools

| Module or Tool                                                                                                                   | Purpose in This Workflow                                                            |
| -------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| [community.proxmox.proxmox_kvm](https://docs.ansible.com/ansible/latest/collections/community/proxmox/proxmox_kvm_module.html)   | Clone and configure QEMU VMs; remove cloud-init device references.                  |
| [community.proxmox.proxmox_disk](https://docs.ansible.com/ansible/latest/collections/community/proxmox/proxmox_disk_module.html) | Resize the boot disk and add optional disks in the native path.                     |
| `ansible.builtin.uri`                                                                                                            | Query Proxmox resources and issue API operations such as VM startup.                |
| `ansible.builtin.wait_for_connection`                                                                                            | Verify the guest connection after startup.                                          |
| `ansible.builtin.raw`                                                                                                            | Poll cloud-init without requiring guest Python.                                     |
| `ansible.builtin.reboot`                                                                                                         | Reboot the guest and verify boot identity and connectivity.                         |
| `ansible.builtin.known_hosts`                                                                                                    | Bootstrap control-node SSH trust for the guest.                                     |
| Terraform with the Telmate Proxmox provider                                                                                      | Create the initial VM, retain ownership state, and execute validated removal plans. |

`community.proxmox.proxmox` manages LXC containers; it is not the general QEMU VM or node/storage query module for this workflow.

---

## 📂 Entry Points

The VM creation playbook selects the backend:

{% raw %}
```text
playbooks/vms/provision_vm.yml
```
{% endraw %}

{% raw %}
```yaml
vms_use_terraform: true   # Terraform + Ansible
vms_use_terraform: false  # Ansible-only
```
{% endraw %}

Limit the operation to the intended host:

{% raw %}
```shell
ansible-playbook -i inventory/test/inventory.ini \
  playbooks/vms/provision_vm.yml --limit test-0
```
{% endraw %}

For the full post-provision workflow, use:

{% raw %}
```shell
ansible-playbook -i inventory/test/inventory.ini \
  playbooks/provision_vm.yml --limit test-0
```
{% endraw %}

The full wrapper additionally runs Python bootstrap, domain join, managed-node preparation, user provisioning, and disk preparation. **Review attached disks first:** the final disk role discovers partitioning/formatting candidates and is not restricted to a declared additional VM disk. Creation-stage idempotence does not make all later stages a safe general maintenance operation.

---

## 🗑️ Safe VM Removal

Use the existing removal playbook and its explicit confirmation:

{% raw %}
```shell
ansible-playbook -i inventory/test/inventory.ini \
  playbooks/vms/remove_vm.yml --limit test-0
```
{% endraw %}

For Terraform-backed guests, removal verifies ownership, validates a confirmed destroy-only plan, and applies that exact plan under the VM workflow lock. It does not stop the guest before those checks. DNS cleanup occurs only after successful removal. Missing configuration or mismatched state fails closed rather than silently skipping deletion.

---

## 🧩 Contributor Notes

- Reuse the shared startup, cloud-init, trust, and checkpoint finalization tasks in both backends.
- Preserve the ownership and saved-plan guards when extending Terraform operations.
- Keep creation and finalization recovery separate so reruns cannot accidentally recreate a guest.
- Do not bypass workflow locks or share a fixed saved-plan filename between attempts.
- Use `vms_name` consistently for Proxmox identity and snippet references.
- Backend creation details differ; shared intent is not a guarantee that every inventory variable is portable.
- Add offline regression coverage before testing live VM lifecycle changes.

Current offline suites include ownership/idempotence, Terraform rendering and plan safety, cloud-init status checks, lock contention, unique-plan cleanup, and finalization recovery. They do not replace live tests of guest startup/reboot, storage behavior, or automation from multiple control nodes.
