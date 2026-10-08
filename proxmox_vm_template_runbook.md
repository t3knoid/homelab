---
title: "Proxmox VM Template Runbook"
---

# 🏃 Proxmox VM Template Runbook

This runbook provides **step-by-step instructions to create an Ubuntu 24.04 Server cloud-init VM template** in the Home Lab. It uses the existing `global` and `cloudinit` roles through the [template creation playbook](../playbooks/template/create_ubuntu_24_04_server_template.yml).

---

## 1️⃣ Login to an Ansible Control Node

Log into a control node with Ansible installed and prepare the environment:

{% raw %}
```shell
cd ~/ansible
source /opt/python_3.12/bin/activate
INV=inventory/template/inventory.ini
```
{% endraw %}

> ⚡ Important: Run all Ansible commands from the control node. The playbook delegates template creation to the configured Proxmox node, not to the placeholder host `ubu24-template`.

---

## 2️⃣ Pull the Latest Code

Check for local changes before updating the repository:

{% raw %}
```shell
git status --short
git pull --ff-only origin main
```
{% endraw %}

Preserve or resolve uncommitted changes before pulling. Confirm the activated environment contains Ansible and the repository's required dependencies.

---

## 3️⃣ Set Template Configuration

Edit [inventory/template/group_vars/all.yml](../inventory/template/group_vars/all.yml). The existing configuration is:

{% raw %}
```yaml
template:
  ubuntu_24_server:
    name: "ubuntu-server-24.04-cloudinit"
    vmid: "9501"
    memory_mb: 2048
    storage: local
    network_device: "virtio,bridge=vmbr0"
    scsi_controller_model: virtio-scsi-pci
    cpu_type: host
    cores: 1
    ostype: l26
    proxmox_node: pve-2
```
{% endraw %}

Set the template name, VMID, storage, memory, network bridge, and Proxmox node to the intended values. `cores` is present in the inventory but is not currently passed to `qm create` by the role; do not rely on changing it to set CPU count.

This playbook uses `ubuntu_24_server`; it is not a generic OS selector. The image URL and filename come from `global_os[cloudinit_template_os]` in the `global` role. Ubuntu publishes cloud images at [cloud-images.ubuntu.com](https://cloud-images.ubuntu.com/noble/current/).

Confirm the configured storage supports VM disks and cloud-init volumes, has sufficient free space, and the configured bridge exists. The Proxmox node needs outbound access to download the image and install `wget` and `libguestfs-tools`. Verify SSH and privilege escalation access from the control node.

> ⚡ Important: Use an unused cluster-wide VMID. The role contains a destructive `qm destroy --purge` step for an existing VMID, guarded by a local disk path. Rerunning against an existing template is not a safe in-place update: it can delete the existing VM/template or fail depending on its storage layout. Back up first and prefer a new VMID when replacing a template.

---

## 4️⃣ Commit Configuration Changes

If you changed the template configuration, commit it before deployment:

{% raw %}
```shell
git add inventory/template/group_vars/all.yml
git commit -m "Configure Ubuntu 24.04 Proxmox template"
git push origin main
```
{% endraw %}

Use the repository's branch and review process when required. Skip this step if no configuration changed.

---

## 5️⃣ Create the Template Using Ansible

Set these shell variables to match the configuration from step 3:

{% raw %}
```shell
PVE_NODE=pve-2
VMID=9501
```
{% endraw %}

Check the intended target and validate playbook syntax:

{% raw %}
```shell
ansible-playbook -i "$INV" \
  playbooks/template/create_ubuntu_24_04_server_template.yml --list-hosts
ansible-playbook -i "$INV" \
  playbooks/template/create_ubuntu_24_04_server_template.yml --syntax-check
```
{% endraw %}

In the Proxmox web UI, check the entire cluster for VMID conflicts. You can also inspect the cluster VM list from the node:

{% raw %}
```shell
ansible "$PVE_NODE" -i inventory/pve/inventory.ini -b \
  -m ansible.builtin.command -a 'cat /etc/pve/.vmlist'
```
{% endraw %}

Proceed only after confirming the selected VMID is unused and the configuration is correct:

{% raw %}
```shell
ansible-playbook -i "$INV" \
  playbooks/template/create_ubuntu_24_04_server_template.yml
```
{% endraw %}

The role downloads the Ubuntu cloud image, creates the VM, imports its disk as `virtio0`, adds a cloud-init drive, configures serial display and boot order, converts the VM to a template, and removes the downloaded image.

> ⚡ Note: Add `-k` if an SSH password is required or `-K` if a privilege escalation password is required.
---

## 6️⃣ Verify Template Creation

1. Open the configured node's Proxmox web UI on HTTPS port `8006`.
2. Locate the configured VMID and confirm its name and template icon.
3. Check that its hardware includes `virtio0`, a cloud-init drive on `ide2`, and serial console settings.

Inspect the resulting configuration from Ansible:

{% raw %}
```shell
ansible "$PVE_NODE" -i inventory/pve/inventory.ini -b \
  -m ansible.builtin.command -a "qm config $VMID"
```
{% endraw %}

Confirm `template: 1`, `boot: order=virtio0`, the intended storage and memory, and the expected network bridge. Clone to a new, unused test VMID and supply the normal cloud-init user, SSH key, and networking settings to verify the guest boots and is reachable. Do not boot or modify the base template to test it.

---

## 7️⃣ Extend to Other OS Cloud Images

Reuse the `cloudinit` role for compatible Linux cloud disk images. An installer ISO is not interchangeable with a cloud image. Choose an image matching the node's architecture and supporting cloud-init, virtio disks/networking, serial console, and the role's default BIOS boot configuration. Images requiring UEFI or other hardware changes need role changes before using this procedure.

The following example adds Ubuntu 22.04 alongside Ubuntu 24.04. These are instructions for a future extension; the example configuration and playbook are not created by this runbook.

### Add Image Metadata

In [roles/global/defaults/main/main.yml](../roles/global/defaults/main/main.yml), add this entry under the existing `global_os` mapping, preserving its other entries and indentation:

{% raw %}
```yaml
ubuntu_22_server:
  distro: ubuntu
  type: server
  cloudinit_download_url: https://cloud-images.ubuntu.com/jammy/current
  cloudinit_img: jammy-server-cloudimg-amd64.img
  template: ubuntu-server-22.04-cloudinit
  version: "22.04"
```
{% endraw %}

The download task combines `cloudinit_download_url` and `cloudinit_img` with `/`. Use the image publisher's official directory and exact filename, and verify its published checksum/signature before deployment. The current role does not perform publisher-checksum validation automatically. Other consumers of `global_os` may need additional fields; the cloud-init creation role requires the two cloud-image fields above.

### Add Template Settings

In [inventory/template/group_vars/all.yml](../inventory/template/group_vars/all.yml), add a matching entry under the existing `template` mapping:

{% raw %}
```yaml
ubuntu_22_server:
  name: "ubuntu-server-22.04-cloudinit"
  vmid: "<unused-vmid>"
  memory_mb: 2048
  storage: local
  network_device: "virtio,bridge=vmbr0"
  scsi_controller_model: virtio-scsi-pci
  cpu_type: host
  ostype: l26
  proxmox_node: pve-2
```
{% endraw %}

Replace `<unused-vmid>` with an unused numeric cluster-wide VMID. The key `ubuntu_22_server` must match the image metadata key exactly. Adjust the storage, bridge, node, and resources using the checks in step 3.

### Add an Inventory Group and Playbook

Append a distinct group to [inventory/template/inventory.ini](../inventory/template/inventory.ini):

{% raw %}
```ini
[ubuntu22]
ubu22-template
```
{% endraw %}

Create a dedicated playbook alongside the [Ubuntu 24.04 example](../playbooks/template/create_ubuntu_24_04_server_template.yml), with this content:

{% raw %}
```yaml
---
# Purpose: Creates an Ubuntu 22.04 Server cloud-init template on Proxmox.

- name: Create an Ubuntu 22.04 Server Template
  hosts: ubuntu22
  gather_facts: false
  become: true
  vars:
    cloudinit_template_os: ubuntu_22_server
  roles:
    - global
    - role: cloudinit
      delegate_to: "{{ template[cloudinit_template_os].proxmox_node }}"
      vars:
        ansible_python_interpreter: /usr/bin/python3
```
{% endraw %}

Save the new playbook at the path used below. Setting `cloudinit_template_os` selects both the image metadata and template settings. The existing Ubuntu 24.04 playbook hardcodes its delegation key, so overriding the selector alone there can select another image but still delegate to Ubuntu 24.04's node. Use the matching selector in the dedicated playbook instead.

### Validate, Commit, Create, and Verify

Validate the extended inventory and new playbook:

{% raw %}
```shell
ansible-inventory -i "$INV" --graph
ansible-playbook -i "$INV" \
  playbooks/template/create_ubuntu_22_04_server_template.yml --list-hosts
ansible-playbook -i "$INV" \
  playbooks/template/create_ubuntu_22_04_server_template.yml --syntax-check
```
{% endraw %}

Commit the image metadata, inventory settings, inventory group, and new playbook using step 4's repository workflow. Repeat the backup, storage, and VMID checks before running:

{% raw %}
```shell
ansible-playbook -i "$INV" \
  playbooks/template/create_ubuntu_22_04_server_template.yml
```
{% endraw %}

Repeat step 6 with the new node and VMID. On a test clone, verify the actual OS release, cloud-init completion, SSH key injection, networking, and guest-agent availability. For another Linux distribution, follow the same matching-key pattern using its official cloud image and test compatibility before adopting the template.

> ⚡ Important: The existing Windows entries in `global_os` describe installer ISOs and do not have the cloud-image fields required by this role. Windows template preparation, drivers, guest customization, and Cloudbase-Init require a separate workflow; changing the selector or setting `ostype` alone is not enough.

---

### ✅ Notes

- This workflow creates an Ubuntu 24.04 cloud-init template, not a running application VM.
- Prefer creating replacements under a new VMID; update clone consumers only after verification.
- Do not blindly rerun a failed creation. Inspect the VMID, disks, and task output first.
- The role enables the Proxmox guest-agent option but its image-customization tasks are commented out; it does not install `qemu-guest-agent` inside the image.
- Check task results and the resulting Proxmox configuration, not only Ansible's changed count: the role marks its `qm` commands as unchanged.
