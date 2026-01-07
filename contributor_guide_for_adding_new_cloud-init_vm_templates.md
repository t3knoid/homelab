---
title: "Contributor Guide for Adding New Cloud-Init VM Templates"
---

# 🧩 Contributor Guide for Adding New Cloud-Init VM Templates

This guide explains exactly what a contributor must do to add support for a new VM template. It focuses on the relationship between `global_os`, template inventory, host‑vars, and the template creation playbook.

---

## 📦 How Template Creation Is Structured

Template creation is orchestrated by:

- **The `global` role** — defines OS metadata in  
  `roles/global/defaults/main/main.yml`
- **The `cloudinit` role** — downloads the cloud image and builds the Proxmox template
- **The template creation playbook**:

  ```yaml
  # playbooks/template/create_template.yml
  - name: Create a Template
    hosts: template
    gather_facts: false
    become: true
    roles:
      - global
      - role: cloudinit
        delegate_to: "{{ cloudinit_proxmox_node }}"
        vars:
          ansible_python_interpreter: /usr/bin/python3
  ```

- **The template inventory**, usually:  
  `inventory/template/inventory.ini`
- **Per‑template host vars**, e.g.:  
  `inventory/template/host_vars/ubu24-template.yml`

These components determine which OS image is used, where the template is created, and what hardware settings the template starts with.

---

## 🗂️ Understanding `global_os` and Why It Matters

`global_os` is the authoritative mapping of all OS families the automation can build.  
Each key (e.g., `ubuntu_24_server`) defines:

- Where to download the cloud image  
- What the cloud image filename is  
- What the template should be named  
- Optional metadata (distro, type, ISO, tarball, version)

Example:

{% raw %}
```yaml
global_os:
  ubuntu_24_server:
    distro: ubuntu
    type: server
    release_download_url: "https://releases.ubuntu.com/noble"
    iso: ubuntu-24.04.1-live-server-amd64.iso
    cloudinit_download_url: https://cloud-images.ubuntu.com/noble/current
    cloudinit_img: noble-server-cloudimg-amd64.img
    tarball: ubuntu-24.04.1-netboot-amd64.tar.gz
    template: ubuntu-server-24.04-cloudinit
    version: 24.4
```
{% endraw %}

The contributor references this OS entry using:

{% raw %}
```yaml
cloudinit_template_os: ubuntu_24_server
```
{% endraw %}

The `cloudinit` role then uses the URLs and filenames to download and import the correct cloud image.

---

## 🛠️ Contributor Checklist: Adding a New Template

### 1. Add a new OS entry to `global_os`

Edit:

{% raw %}
```
roles/global/defaults/main/main.yml
```
{% endraw %}

Add a new block following the existing structure:

{% raw %}
```yaml
global_os:
  my_new_os:
    distro: ubuntu
    type: server
    release_download_url: "https://releases.ubuntu.com/<release>"
    iso: <installer ISO name>
    cloudinit_download_url: https://cloud-images.ubuntu.com/<release>/current
    cloudinit_img: <cloud image filename>
    tarball: <optional netboot tarball>
    template: <proxmox-template-name>
    version: <version number>
```
{% endraw %}

**Required:** `cloudinit_download_url`, `cloudinit_img`, `template`, `version`  
**Optional:** everything else

---

### 2. Create a host‑vars file for the new template

Location:

{% raw %}
```
inventory/template/host_vars/<template-name>.yml
```
{% endraw %}

Example:

{% raw %}
```yaml
cloudinit_template_os: my_new_os
cloudinit_template_name: ubuntu-24.04-cloudinit
cloudinit_vmid: 9024
cloudinit_proxmox_node: proxmox01.example.local

# Hardware defaults
cloudinit_storage: local-lvm
cloudinit_network_device: "virtio,bridge=vmbr0"
cloudinit_memory_mb: 2048
```
{% endraw %}

---

## ⚙️ Important: Define Hardware at the Smallest Acceptable Baseline

Template hardware **must always be minimal**, because:

- Templates are cloned into new VMs  
- New VMs can **expand** CPU, memory, and disk during provisioning  
- Over‑provisioned templates force every clone to start oversized  
- Minimal templates reduce storage footprint and speed up cloning

**Contributor rule:**  
> When defining template hardware (memory, CPU type, disk size), choose the smallest configuration that still boots and supports cloud‑init.

This ensures downstream provisioning can scale hardware upward as needed.

---

### 3. Add the template host to the template inventory

Edit:

{% raw %}
```
inventory/template/inventory.ini
```
{% endraw %}

Example:

{% raw %}
```ini
[template]
ubu24-template ansible_host=proxmox01.example.local
```
{% endraw %}

The hostname must match the host‑vars filename.

---

### 4. Run the template creation playbook

{% raw %}
```bash
ansible-playbook playbooks/template/create_template.yml \
  -i inventory/template/inventory.ini
```
{% endraw %}

The playbook loads your new `global_os` entry, applies the host‑vars, and builds the template on the specified Proxmox node.

---

## 🧭 Summary for Contributors

To add a new template:

1. **Define the OS** in `global_os`  
2. **Create host‑vars** for the template  
3. **Use minimal hardware settings**  
4. **Add the template host** to the template inventory  
5. **Run the template creation playbook**

This keeps the system consistent, predictable, and easy to extend.

