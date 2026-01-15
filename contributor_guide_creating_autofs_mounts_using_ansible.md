---
title: "Contributor Guide: Creating Autofs Mounts Using Ansible"
---

# 📦 Contributor Guide: Creating Autofs Mounts Using Ansible

The `autofs` role installs and configures the **autofs automounter** on Debian/Ubuntu systems. Autofs provides transparent, on-demand NFS mounts—filesystems are mounted automatically when accessed and unmounted after a period of inactivity.

This makes it ideal for:

* Large numbers of NFS shares
* Environments where boot-time mounts cause delays
* Media servers and shared resources

🔗 **Source repository:**
👉 [https://github.com/t3knoid/ansible/tree/main/roles/autofs](https://github.com/t3knoid/ansible/tree/main/roles/autofs)

---

## ✨ Key Features

* **Automatic NFS mounting** – Mounts appear instantly on access
* **Automatic unmounting** – Frees resources after idle timeout
* **Transparent to users** – No manual mount/unmount required
* **Scalable** – Efficiently handles dozens or hundreds of NFS shares
* **Service-based** – Managed via the autofs daemon
* **Dynamic configuration** – Add or remove mounts without reboots

---

## 🧰 Prerequisites

* Target OS: **Debian or Ubuntu**
* Minimum Ansible version: **2.9**
* Network access to NFS servers
* Root or `become` access on target hosts

---

## ⚙️ Variables

### 🔴 Required

* `autofs_nfs_mounts` (list): Array of NFS mount definitions.
  Each entry must include:

  * `mount_name` (string): Short name used in the mount path
  * `server` (string): NFS export in `server:/path` format
  * `mount_options` (string): NFS mount options (**leading `-` required**)

### 📐 Mount Structure

Each mount follows this structure:

{% raw %}
```yaml
- mount_name: music
  server: 192.168.2.250:/mnt/Data/music
  mount_options: -rw,relatime,hard,rsize=1048576,wsize=1048576,proto=tcp,timeo=600,retrans=2,sec=sys
```
{% endraw %}

---

## 🧠 How It Works

### 🏗 Autofs Architecture

Autofs relies on a hierarchical configuration model:

1. **Master map** (`/etc/auto.master`)
   Defines base mount points and associated automount maps
2. **Automount map** (`/etc/auto.nfs`)
   Lists individual NFS mounts and their options
3. **Autofs daemon**
   Monitors access and mounts/unmounts filesystems dynamically

### 🔁 Role Execution Flow

1. Install the `autofs` package
2. Configure `/etc/auto.master` with a `/nfs` base path
3. Populate `/etc/auto.nfs` with defined NFS mounts
4. Enable and start the autofs service

### 🗂 Mount Path Generation

Mount paths are generated automatically:

* Base path: `/nfs`
* Mount name: `music`
* **Resulting path:** `/nfs/music`

---

## 🚀 Usage Examples

### 🟢 Basic NFS Mounts

{% raw %}
```yaml
- hosts: media_servers
  become: true
  roles:
    - autofs
  vars:
    autofs_nfs_mounts:
      - mount_name: photos
        server: 192.168.2.240:/volume1/Photos
        mount_options: -rw,relatime,hard,rsize=1048576,wsize=1048576,proto=tcp,timeo=600,retrans=2,sec=sys
      - mount_name: music
        server: 192.168.2.250:/mnt/Data/music
        mount_options: -rw,relatime,hard,rsize=1048576,wsize=1048576,proto=tcp,timeo=600,retrans=2,sec=sys
```
{% endraw %}

### 🗃 With Group Variables

{% raw %}
```yaml
# inventory/media/group_vars/all/main.yml
autofs_nfs_mounts:
  - mount_name: photos
    server: 192.168.2.240:/volume1/Photos
    mount_options: -rw,relatime,hard,rsize=1048576,wsize=1048576,proto=tcp,timeo=600,retrans=2,sec=sys
  - mount_name: music
    server: 192.168.2.250:/mnt/Data/music
    mount_options: -rw,relatime,hard,rsize=1048576,wsize=1048576,proto=tcp,timeo=600,retrans=2,sec=sys
  - mount_name: books
    server: 192.168.2.250:/mnt/Data/books
    mount_options: -rw,relatime,hard,rsize=1048576,wsize=1048576,proto=tcp,timeo=600,retrans=2,sec=sys
```
{% endraw %}

Then reference the role:

{% raw %}
```yaml
- hosts: media_servers
  become: true
  roles:
    - autofs
```
{% endraw %}

---

## 📁 Configuration Files

### `/etc/auto.master`

{% raw %}
```text
/nfs    /etc/auto.nfs
```
{% endraw %}

Defines:

* `/nfs` as the base mount directory
* `/etc/auto.nfs` as the automount map

### `/etc/auto.nfs`

{% raw %}
```text
# {mark} ANSIBLE MANAGED BLOCK
photos -rw,relatime,hard,... 192.168.2.240:/volume1/Photos
music  -rw,relatime,hard,... 192.168.2.250:/mnt/Data/music
books  -rw,relatime,hard,... 192.168.2.250:/mnt/Data/books
# {mark} ANSIBLE MANAGED BLOCK
```
{% endraw %}

Uses `blockinfile` markers to ensure **idempotent updates**.

---

## 🧩 Task Breakdown

### 1️⃣ Install autofs

* Installs the package
* Updates the package cache

### 2️⃣ Configure auto.master

* Deploys template
* Sets ownership and permissions
* Triggers restart on change

### 3️⃣ Manage auto.nfs

* Uses `blockinfile`
* Preserves unmanaged entries
* Triggers restart on change

### 🔄 Restart Handler

* Restarts autofs only when configuration changes occur

---

## 🧹 Removal Task

Optional uninstall via `remove.yml`:

{% raw %}
```yaml
- name: Remove autofs
  ansible.builtin.include_tasks: "roles/autofs/tasks/remove.yml"
```
{% endraw %}

Actions:

* Stops and disables autofs
* Removes the package
* Cleans up configuration files

---

## 📚 Ansible Module References

* `ansible.builtin.apt`
* `ansible.builtin.template`
* `ansible.builtin.blockinfile`
* `ansible.builtin.service`

---

## 📌 Examples in Repository

* `inventory/semaphore/group_vars/all/main.yml`
* `playbooks/grafana/create_db.yml`

