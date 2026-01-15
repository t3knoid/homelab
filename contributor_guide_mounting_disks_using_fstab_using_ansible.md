---
title: "Contributor Guide: Mounting Disks Using fstab Using Ansible"
---

# 🧩 **Contributor Guide: Mounting Disks Using fstab Using Ansible**

The `fstab` role provides a **declarative**, **idempotent**, and **state‑aware** way to manage filesystem mounts via `/etc/fstab`. Unlike traditional approaches that only append entries, this role ensures the system’s mount configuration matches your desired state exactly—adding new mounts and removing those no longer defined.

👉 Browse the role on GitHub: https://github.com/t3knoid/ansible/tree/main/roles/fstab

Unlike **[autofs](autofs.md)**, which performs on‑demand NFS automounting, this role uses **static `/etc/fstab` entries**, making it suitable for both NFS and local disk mounts.

---

## ⭐ **Key Features**

- **Declarative** — Define desired mounts; the role enforces that state  
- **Idempotent** — Safe to run repeatedly; only changes when needed  
- **State‑aware removal** — Removes only mounts previously managed by this role  
- **Mount verification** — Confirms a mount is active before unmounting  
- **Supports multiple filesystem types** — NFS, ext4, xfs, vfat, and more  
- **Persistent mounts** — Ensures mounts survive reboots via `/etc/fstab`

---

## 🧰 **Prerequisites**

- Target system must be Linux‑based (Debian/Ubuntu recommended)  
- Install the required collection:  
  ```bash
  ansible-galaxy collection install ansible.posix
  ```

---

## 📝 **Variables**

### 🔸 Required

`fstab_mounts` (list): Array of mount configurations. Each entry must include:

- `device` — Device path or NFS export  
  - Local: `/dev/sdb1`, `/dev/vdc1`  
  - NFS: `192.168.2.240:/volume1/Photos`, `nfs-server:/export/share`
- `mount_point` — Local mount path (e.g., `/data`, `/nfs/music`)

### 🔹 Optional

| Parameter | Type | Default | Description |
|----------|------|---------|-------------|
| `fstype` | string | `ext4` | Filesystem type (`nfs`, `ext4`, `xfs`, etc.) |
| `opts` | string | `defaults` | Mount options (comma‑separated) |
| `boot` | boolean | `true` | Mount at system startup |

---

## ⚙️ **How It Works**

The role maintains **declarative state** by tracking which mounts it manages. On each run:

1. **Initialize** — Load defaults and prepare variables  
2. **Calculate changes** — Compare defined mounts vs. previously managed ones  
3. **Remove old mounts**  
   - Check if mounted  
   - Unmount  
   - Remove `/etc/fstab` entry  
   - Delete mount directory  
4. **Add/update mounts**  
   - Create mount directory  
   - Add/update `/etc/fstab` entry  
   - Mount the filesystem  

### 🧠 State Tracking

The role uses the fact `fstab_mounts_managed` to track previously managed mount points. This ensures:

- Only mounts created by this role are removed  
- Manually managed mounts remain untouched  
- Behavior is consistent across runs  

---

## 📦 **Examples**

### 📁 Basic NFS Mounts

{% raw %}
```yaml
- hosts: media_servers
  become: true
  roles:
    - fstab
  vars:
    fstab_mounts:
      - device: "192.168.2.240:/volume1/Photos"
        mount_point: "/nfs/photos"
        fstype: "nfs"
        opts: "rw,relatime,hard,rsize=1048576,wsize=1048576,proto=tcp,timeo=600,retrans=2,sec=sys"
      - device: "192.168.2.250:/mnt/Data/music"
        mount_point: "/nfs/music"
        fstype: "nfs"
        opts: "rw,relatime,hard,rsize=1048576,wsize=1048576,proto=tcp,timeo=600,retrans=2,sec=sys"
```
{% endraw %}

### 💽 Local Disk Mounts

{% raw %}
```yaml
fstab_mounts:
  - device: "/dev/sdb1"
    mount_point: "/data"
    fstype: "ext4"
    opts: "defaults,nofail"
  - device: "/dev/sdc1"
    mount_point: "/backup"
    fstype: "ext4"
    opts: "defaults,noatime"
```
{% endraw %}

### 🔀 Mixed Mount Types

{% raw %}
```yaml
fstab_mounts:
  - device: "/dev/sdb1"
    mount_point: "/local-storage"
    fstype: "ext4"
  - device: "nfs-server:/export"
    mount_point: "/remote-storage"
    fstype: "nfs"
    opts: "rw,sync,hard,intr"
  - device: "/dev/sdc1"
    mount_point: "/backup"
    fstype: "xfs"
    opts: "defaults"
```
{% endraw %}

### 🔁 Idempotent Changes Example

**First run** — three mounts defined → all created and mounted  
**Second run** — remove `/nfs/photos` → unmounted, removed from fstab, directory deleted  
**Third run** — no changes → system already matches desired state  

---

## 🔧 **Common Mount Options**

### 📡 NFS Options

{% raw %}
```
rw                 # Read-write
relatime           # Efficient access-time updates
hard               # Retry indefinitely on timeout
soft               # Fail after timeout
rsize=1048576      # Read buffer (1MB)
wsize=1048576      # Write buffer (1MB)
proto=tcp          # TCP transport
timeo=600          # Timeout (60s)
retrans=2          # Retries
sec=sys            # UNIX auth
nofail             # Don’t fail boot if unavailable
```
{% endraw %}

### 💾 Local Filesystem Options

{% raw %}
```
defaults           # Standard options
noatime            # Improve performance
relatime           # Efficient access-time updates
nofail             # Don’t fail boot
noexec             # Prevent execution
nosuid             # Disable setuid/setgid
nodev              # Ignore device files
```
{% endraw %}

---

## 🛠 **Task Breakdown**

### 1️⃣ Initialize & Calculate  
- Apply defaults  
- Determine removed mounts  
- Update managed list  

### 2️⃣ Remove Old Mounts  
- Verify mount status  
- Unmount if needed  
- Remove fstab entry  
- Delete directory  

### 3️⃣ Add/Update Mounts  
- Create mount directories  
- Add/update fstab entries  
- Mount filesystems  

---

## 📚 **Ansible Module References**

- `ansible.builtin.file` — directory management  
- `ansible.posix.mount` — fstab + mount control  
- `ansible.builtin.command` — mountpoint checks  
- `ansible.builtin.set_fact` — state tracking  
