---
title: "Provision a New Virtual Machine Runbook"
---

# 🏃 Provision a New Virtual Machine Runbook

This runbook provides **step-by-step instructions to deploy or update a virtual machine** in the Home Lab. It references the `playbooks/provision_vm.yml` Ansible playbook and ensures consistency, verification, and version control.

The virtual machine provisioning playbook creates a new virtual machine, installs Python so Ansible can manage it, joins the VM to the Active Directory domain, applies the standard baseline configuration for Ansible nodes, provisions required users, and prepares any additional disks for use. The result is a fully initialized, domain‑joined, Ansible‑ready VM with correct hardware, networking, users, and storage—ready for role‑specific configuration or application deployment.

---

## 1️⃣ Login to an Ansible Control Node

Start by logging into a control node with Ansible installed and prepare the environment:

{% raw %}
```shell
cd ~/ansible
source /opt/python_3.12/bin/activate
INV=inventory/test/inventory.ini
```
{% endraw %}

> ⚡ Important: Always start on the control node so all subsequent commands run in the correct environment.

---

## 2️⃣ Pull the Latest Code

Ensure your local repository is up to date:

{% raw %}
```shell
git pull origin main
```
{% endraw %}

> ⚡ Important: Pulling the latest code first prevents conflicts and ensures you’re working with the most recent version.

---

## 3️⃣ Define the Host and Related Properties

Provisioning a new VM requires updating **three configuration locations**:

---

### **A. Define the host in the Inventory**

Edit:

{% raw %}
```
inventory/test/inventory.ini
```
{% endraw %}

Add the host under the `[vms]` group:

{% raw %}
```ini
[vms]
test-01 vms_proxmox_node=pve-1
```
{% endraw %}

---

### **B. Add the Hosts' Assigned IP Address into the Global Vars File**

Edit:

{% raw %}
```
roles/global/vars/main.yml
```
{% endraw %}

Add the mapping:

{% raw %}
```yaml
global_ip_addresses:
  test-01: 192.168.2.210
```
{% endraw %}

---

### **C. Define VM Hardware & OS Configuration in the Inventory**

Create or edit:

{% raw %}
```
inventory/test/host_vars/test-01.yml
```
{% endraw %}

Set the variable:

{% raw %}
```
vms_config
```
{% endraw %}

to the desired hardware configuration.  
Example:

{% raw %}
```yaml
vms_config:
  agent: "1"
  cores: "2"
  cpu: host
  memory: 1024
  ostype: l26
  scsihw: virtio-scsi-single
  sockets: 1
  storage: local

  disk_os:
    disk: virtio0
    backup: true
    size: 20
    storage: local
    format: qcow2

  nic0:
    model: virtio
    bridge: vmbr0

  boot_order: "order=virtio0"

  disk2:
    disk: virtio1
    storage: local-lvm
    size: 20

vms_os: ubuntu_24_server
vms_autoinstall: true
vms_enable_serial_terminal: false
vms_additional_packages: []
```
{% endraw %}

---

### **D. `vms_config` Parameter Reference Table**

| Parameter | Description |
|----------|-------------|
| `agent` | Enables QEMU guest agent (`1` = enabled). |
| `cores` | Number of CPU cores. |
| `sockets` | Number of CPU sockets. |
| `cpu` | CPU type passed to Proxmox (e.g., `host`). |
| `memory` | RAM in MB. |
| `ostype` | OS type identifier (`l26` for Linux). |
| `scsihw` | SCSI controller type. |
| `storage` | Default storage pool for disks. |
| `disk_os.disk` | Device name for OS disk (e.g., `virtio0`). |
| `disk_os.size` | Disk size in GB. |
| `disk_os.storage` | Storage pool for OS disk. |
| `disk_os.backup` | Whether disk is included in backups. |
| `disk_os.format` | Disk format (`qcow2`, `raw`). |
| `nic0.model` | NIC model (usually `virtio`). |
| `nic0.bridge` | Proxmox bridge (e.g., `vmbr0`). |
| `boot_order` | Boot device order. |
| `disk2.*` | Optional additional disk configuration. |
| `vms_os` | OS template identifier. |
| `vms_autoinstall` | Enables unattended autoinstall. |
| `vms_enable_serial_terminal` | Enables serial console. |
| `vms_additional_packages` | Extra packages installed during autoinstall. |

> Note: Use the same process for updates as for new deployments.

---

## 4️⃣ Commit Configuration Changes

After modifying the configuration, commit your changes:

{% raw %}
```shell
git add inventory/test/
git add roles/global/vars/main.yml
git commit -m "Provision new VM test-01 with defined hardware and IP"
git push origin main
```
{% endraw %}

> ⚡ Important: Replace `test-01` with the actual VM name.

---

## 5️⃣ Deploy Using Ansible Playbook

Run the provisioning playbook:

{% raw %}
```shell
ansible-playbook -i $INV playbooks/provision_vm.yml -k
```
{% endraw %}

> ⚡ Note: Use `-k` if prompted for SSH password.

---

## 6️⃣ Verify Deployment

After deployment:

1. Log into Proxmox.
2. Confirm the VM **exists**, is **powered on**, and has the correct hardware.
3. Verify the assigned IP matches the value in `global_ip_addresses`.
4. If autoinstall is enabled, confirm the OS installation completes successfully.

---

### ✅ Notes

* Always double-check the VM name, IP address, and hardware configuration before deploying.
* Use this workflow for both **new VM provisioning** and **hardware updates**.
* Ensure the control node has network access to the Proxmox cluster.
* Pulling, committing, and deploying in this order prevents repository conflicts and ensures a consistent deployment state.