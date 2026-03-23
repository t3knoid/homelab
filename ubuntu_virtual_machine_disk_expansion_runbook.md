---
title: "️ Ubuntu Virtual Machine Disk Expansion Runbook"
---

# 🖥️ Ubuntu Virtual Machine Disk Expansion Runbook 

This guide documents how to **increase the disk size of an Ubuntu virtual machine** hosted in Proxmox.  It covers:

- Expanding the virtual disk in Proxmox  
- Expanding partitions and filesystems inside Ubuntu  
- Separate procedures for **LVM** and **Non‑LVM** systems  

---

## ⚡ Quick Guide

Before choosing a workflow, identify your disk layout:

{% raw %}
```shell
sudo lsblk
```
{% endraw %}

| If you see… | Example | Use… |
|-------------|---------|------|
| LVM volumes (`ubuntu--vg-ubuntu--lv`, `/dev/mapper/...`) | `/dev/sda3` → PV → VG → LV | **Path A: LVM Expansion** |
| A single root partition (`/dev/sda1`, `/dev/vda1`) with no LVM | `/dev/vda1` mounted on `/` | **Path B: Non‑LVM Expansion** |

---

# 1️⃣ Increase the Virtual Machine Disk in Proxmox

| Step | Action | Notes |
|------|--------|-------|
| 1 | Shut down the VM | Ensure the VM is powered off |
| 2 | Go to **Hardware** tab | Select the VM in Proxmox |
| 3 | Select the disk → **Disk Action → Resize** | Enter the size increment in GiB |
| 4 | Click **Resize Disk** | Wait for the operation to complete |

> ⚡ Do not boot the VM until the resize is finished.

---

# 2️⃣ Expand the Disk Inside Ubuntu  
After booting the VM, follow **either Path A (LVM)** or **Path B (Non‑LVM)**.

---

# 🟩 **Path A — LVM-Based Root Filesystem Expansion**  
*(Use this if your root filesystem is on LVM.)*

### A.1 Verify Disk Layout
{% raw %}
```shell
sudo lsblk
```
{% endraw %}

Example:
{% raw %}
```
sda
├─sda1
├─sda2
└─sda3  → LVM PV
   └─ubuntu--vg-ubuntu--lv  → root filesystem
```
{% endraw %}

---

### A.2 Grow the Partition
{% raw %}
```shell
sudo growpart /dev/sda 3
```
{% endraw %}

---

### A.3 Resize the Physical Volume
{% raw %}
```shell
sudo pvresize /dev/sda3
```
{% endraw %}

---

### A.4 Extend the Logical Volume
{% raw %}
```shell
sudo lvextend -l +100%FREE /dev/mapper/ubuntu--vg-ubuntu--lv
```
{% endraw %}

---

### A.5 Resize the Filesystem
{% raw %}
```shell
sudo resize2fs /dev/mapper/ubuntu--vg-ubuntu--lv
```
{% endraw %}

---

### A.6 Verify the New Size
{% raw %}
```shell
df -h
```
{% endraw %}

---

# 🟦 **Path B — Non‑LVM Root Filesystem Expansion**  
*(Use this if your root filesystem is a normal partition like `/dev/vda1` or `/dev/sda1`.)*

### B.1 Verify Disk Layout
{% raw %}
```shell
sudo lsblk
```
{% endraw %}

Example:
{% raw %}
```
vda
├─vda1   /        ← root filesystem (non‑LVM)
├─vda14
├─vda15  /boot/efi
└─vda16  /boot
```
{% endraw %}

---

### B.2 Grow the Root Partition
Replace `1` with your actual partition number.

{% raw %}
```shell
sudo growpart /dev/vda 1
```
{% endraw %}

---

### B.3 Resize the Filesystem  
For ext4 (Ubuntu default):

{% raw %}
```shell
sudo resize2fs /dev/vda1
```
{% endraw %}

For XFS:

{% raw %}
```shell
sudo xfs_growfs /
```
{% endraw %}

---

### B.4 Verify the New Size
{% raw %}
```shell
df -h
```
{% endraw %}

---

# ✅ Notes

- Always back up important data before resizing disks.  
- LVM and non‑LVM workflows are **not interchangeable**.  
- The correct path depends entirely on what `lsblk` shows.  
- Step order matters:  
  - **LVM:** grow partition → pvresize → lvextend → resize filesystem  
  - **Non‑LVM:** grow partition → resize filesystem
