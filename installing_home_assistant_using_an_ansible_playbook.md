---
title: "Installing Home Assistant Using Ansible"
---

# 🏠 Installing Home Assistant Using Ansible

This document explains the **Home Assistant setup role** in Ansible. It deploys **Home Assistant OS** into a **Proxmox Virtual Environment**. Designed for contributors familiar with Ansible, it provides a fast onboarding without diving into the code.

---

## 🔍 Where to Look

Key files for the role:

* `roles/home_assistant_setup/tasks/main.yml` — main tasks
* `roles/home_assistant_setup/handlers/main.yml` — handlers for image import and VM events
* `roles/home_assistant_setup/defaults/main.yml` — default variables

---

## ⚙️ Key Variables

| Variable                                                                                                                                           | Purpose                                               |
| -------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| `vms_proxmox_node`                                                                                                                                 | Proxmox node to delegate commands                     |
| `global_proxmox_api_*`                                                                                                                             | Proxmox API credentials (host/user/password or token) |
| `vms_vmid`                                                                                                                                         | Optional VMID; otherwise nextid is requested          |
| `vms_vmname`, `vms_config.*`                                                                                                                       | VM creation options (CPU, memory, network, etc.)      |
| `home_assistant_setup_disk_storage`, `home_assistant_setup_qcow2_image_url`, `home_assistant_setup_qcow2_image_xz`, `home_assistant_setup_version` | Image and storage settings                            |

---

## 🔄 High-Level Flow

1. **Get VMID:** Fetch next VMID (`pvesh /cluster/nextid`) → set `home_assistant_setup_vmid`.
2. **Check VM:** Query Proxmox (`proxmox_vm_info`). If VM exists, extract MAC from `config.net0`.
3. **Create VM:** If missing, create a minimal VM → notify handlers to download, decompress, import, and attach QCOW2 image.
4. **Start VM:** Boot the VM.
5. **Discover IP:** Use QEMU guest agent to find VM IP via MAC.
6. **Wait for HA:** Poll Home Assistant HTTP endpoint (`port 8123`) until it returns HTTP 200.

---

## 🛠 Hardcoded VM Parameters (Do Not Change)

| Parameter          | Value               | Why it matters                                     |
| ------------------ | ------------------- | -------------------------------------------------- |
| `machine`          | q35                 | Modern PCIe platform required by HA OS             |
| `scsihw`           | virtio-scsi-single  | Disk visibility for imported QCOW2                 |
| `bios`             | ovmf                | UEFI firmware needed by HA OS                      |
| `ostype`           | l26                 | Linux guest OS hint                                |
| `serial.serial0`   | socket              | Serial console backend                             |
| `vga`              | serial0             | Maps VGA to serial console                         |
| `net.net0`         | virtio,bridge=vmbr0 | Network type/bridge; critical for DHCP/guest-agent |
| `efidisk0.format`  | raw                 | EFI disk format                                    |
| `efidisk0.efitype` | 2m                  | EFI disk size/type for UEFI variables              |

> ⚠️ HA OS requires **UEFI + q35 + virtio devices + virtio-scsi**. Changing these may prevent boot, disk visibility, or IP detection.

---

## 🌐 Finding the VM IP Address

1. Role records VM MAC in `home_assistant_setup_vm_mac_address`

   * From existing `config.net0` if VM exists
   * From create result `mac.net0` if created
2. Delegates to `vms_proxmox_node`:

   ```bash
   qm guest cmd <vmid> network-get-interfaces
   ```
3. Match `hardware-address` (lowercased) → pick first IPv4 from `ip-addresses`.

**Jinja Expression for IPv4 Extraction:**

{% raw %}
```yaml
- home_assistant_setup_vm_interfaces.stdout | default('[]') | from_json
  | selectattr('hardware-address', 'equalto', (home_assistant_setup_vm_mac_address | lower | trim))
  | map(attribute='ip-addresses')
  | flatten
  | selectattr('ip-address-type', 'equalto', 'ipv4')
  | map(attribute='ip-address')
  | first
```
{% endraw %}

---

## ⏳ Waiting for Home Assistant

1. Poll `qm guest cmd <vmid> network-get-interfaces` until stdout contains `ip-address` (retries: 30, delay: 5s)
2. Match VM MAC → extract first IPv4
3. Poll `http://<ip>:8123/` via `ansible.builtin.uri` until HTTP 200 (retries: 30, delay: 10s)
4. On success:

   ```
   Home Assistant is accessible at http://<ip>:8123/
   ```

---

## 🛠 Notes & Troubleshooting

* Requires **QEMU guest agent** in VM; IP detection fails otherwise.
* VM must get DHCP on configured bridge (`vmbr0`) for discovery.
* Image download/import runs **only on VM creation**. Remove VM or change VMID to re-import.
* Adjust retries/delay for slow environments.
* Debug tips:

  ```bash
  qm guest cmd <vmid> network-get-interfaces
  ```

  Inspect handlers for QCOW2 download/import output.

---

## 📦 Minimal Usage Example

{% raw %}
```yaml
- hosts: proxmox
  vars:
    vms_proxmox_node: proxmox-node1
    global_proxmox_api_host: https://proxmox.example.local:8006
    global_proxmox_api_user: root@pam
    global_proxmox_api_password: "REDACTED"
  roles:
    - role: home_assistant_setup
```
{% endraw %}

---

## 📂 Relevant Files

* `roles/home_assistant_setup/tasks/main.yml`
* `roles/home_assistant_setup/handlers/main.yml`
* `roles/home_assistant_setup/defaults/main.yml`

