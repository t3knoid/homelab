---
title: "Provisioning New Virtual Machines Using Ansible"
---

# 🧭 Provisioning New Virtual Machines Using Ansible

This role implements a **cloud‑init–driven VM provisioning pipeline** on Proxmox.  It combines:

- Proxmox API calls  
- Cloud‑init metadata injection  
- Optional disk provisioning  
- Controlled boot sequencing  
- Post‑provision cleanup and SSH hardening  

The workflow is modular, predictable, and designed for contributors to extend safely.

---

# 🧱 Core Architectural Concepts

## 1. Template‑Driven Provisioning

All VMs are created by cloning a pre‑built Proxmox template.  

This ensures:

- Consistent base OS  
- Predictable disk layout  
- Fast provisioning  
- Cloud‑init compatibility  

The template acts as the “golden image” for all new VMs.

---

## 2. Cloud‑Init as the Configuration Engine

Cloud‑init is responsible for configuring the VM on first boot.  

The role generates:

- `user-data` (users, SSH keys, packages, commands)
- `meta-data` (instance ID, hostname)
- Optional snippets (network config, write_files, etc.)

These are injected into the VM via a cloud‑init disk.

Cloud‑init handles all guest‑side configuration, keeping the Ansible controller stateless.

---

## 3. Proxmox API Orchestration

The role interacts with Proxmox to:

- Clone the VM  
- Configure CPU, RAM, disks, NICs  
- Attach cloud‑init resources  
- Migrate the VM between nodes  
- Start, stop, and reboot the VM  

This is done using the **community.proxmox** Ansible collection.

---

## 4. Optional Resource Provisioning

The architecture supports optional components such as:

- Additional disks  
- Node‑specific placement (migration)
- Storage‑specific placement  
- Custom cloud‑init snippets  

This makes the system flexible without complicating the core workflow.

---

## 5. Boot Sequencing and State Validation

The workflow ensures the VM is fully configured before continuing:

1. Boot VM  
2. Wait for cloud‑init to finish  
3. Remove cloud‑init disk  
4. Reboot into final state  

This prevents race conditions and ensures the VM is stable before post‑provision tasks.

---

## 6. SSH Hardening

After provisioning:

- The VM’s SSH host key is added to `known_hosts`
- Future automation runs without prompts or warnings

This is essential for secure, unattended automation.

---

## 🔌 Ansible Modules Used to Interface with Proxmox


## 📦 Proxmox‑Related Ansible Modules

| Module Name | Primary Uses | Documentation |
|------------|--------------|---------------|
| **community.proxmox.proxmox_kvm** | - Clone VMs<br>- Configure CPU, RAM, disks, NICs<br>- Manage cloud‑init settings<br>- Start/stop VMs | https://docs.ansible.com/ansible/latest/collections/community/proxmox/proxmox_kvm_module.html |
| **community.proxmox.proxmox** | - General Proxmox API interactions<br>- Query nodes<br>- Query storage<br>- VM lifecycle operations | https://docs.ansible.com/ansible/latest/collections/community/proxmox/proxmox_module.html |

---

# 🧩 How the Pieces Fit Together

Here’s a diagram of the provisioning pipeline:

{% raw %}
```
┌───────────────────────────┐
│   Generate cloud-init     │
│        snippets           │
│  (user-data, meta-data)   │
└──────────────┬────────────┘
               │
               ▼
┌──────────────────────────┐
│   Clone VM from template │
└──────────────┬───────────┘
               │
               │
               │   ┌──────────────────────────────┐
               └──▶│  Optional: migrate VM to     │
                   │  correct node/storage        │
                   └──────────────┬───────────────┘
                                  │
                                  ▼
                     ┌──────────────────────────┐
                     │ Attach cloud-init disk   │
                     │  (inject snippets)       │
                     └──────────────┬───────────┘
                                    │
                                    ▼
                     ┌──────────────────────────┐
                     │        Start VM          │
                     │ (cloud-init begins)      │
                     └──────────────┬───────────┘
                                    │
                                    ▼
                     ┌──────────────────────────┐
                     │ Wait for cloud-init to   │
                     │        complete          │
                     └──────────────┬───────────┘
                                    │
                                    ▼
                     ┌──────────────────────────┐
                     │ Remove cloud-init disk   │
                     └──────────────┬───────────┘
                                    │
                                    ▼
                     ┌──────────────────────────┐
                     │        Reboot VM         │
                     │ (finalize configuration) │
                     └──────────────┬───────────┘
                                    │
                                    ▼
                     ┌──────────────────────────┐
                     │   Update known_hosts     │
                     │  (SSH trust bootstrap)   │
                     └──────────────┬───────────┘
                                    │
                                    ▼
                     ┌─────────────────────────────┐
                     │ VM ready for post‑provision │
                     │  (Python bootstrap, venv,   │
                     │   agents, config mgmt, etc.)│
                     └─────────────────────────────┘
```
{% endraw %}

This architecture keeps:

- Proxmox operations on the Proxmox side  
- Guest configuration inside cloud‑init  
- Orchestration logic inside Ansible  
- Post‑provision automation clean and predictable