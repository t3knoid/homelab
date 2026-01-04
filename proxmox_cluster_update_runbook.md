---
title: "️ Proxmox Cluster Update Runbook"
---

# 🖥️ Proxmox Cluster Update Runbook

**Description:**  
Step‑by‑step instructions to safely update a three‑node Proxmox cluster using Ceph storage.  
This runbook ensures node‑by‑node updates, VM evacuation, Ceph health validation, and post‑update checks.

---

## 🧭 Prerequisites

- You must have SSH access to all Proxmox nodes.  
- Ensure the cluster is healthy:  
  ```shell
  pvecm status
  ceph -s
  ```
- Confirm Ceph is **HEALTH_OK** before starting.

---

## 🧩 Cluster Overview

The cluster consists of:

- **pve‑0**
- **pve‑1**
- **pve‑2**

**Update order:**

1. **pve‑2**  
2. **pve‑1**  
3. **pve‑0**

Only update **one node at a time**.

---

## 🚦 Step 1 — Log In to the Node

SSH into the node you are updating:

{% raw %}
```shell
ssh root@pve-2
```
{% endraw %}

(Replace with the appropriate node.)

---

## 🚚 Step 2 — Migrate Virtual Machines Off the Node

Migrate all VMs to another node (example: migrate to **pve‑0**):

{% raw %}
```shell
for vm in $(sudo qm list | awk '{print $1}' | tail -n +2); do
    sudo qm migrate "$vm" pve-0 --online
done
```
{% endraw %}

### Verify VM migration

- On the node being updated:  
  ```shell
  qm list
  ```  
  → Should show **no VMs**.

- On the target node:  
  ```shell
  qm list
  ```  
  → Should show the migrated VMs.

---

## 📦 Step 3 — Update Package List

{% raw %}
```shell
sudo apt-get update
```
{% endraw %}

---

## ⬆️ Step 4 — Upgrade Installed Packages

{% raw %}
```shell
sudo apt-get dist-upgrade
```
{% endraw %}

---

## 🔁 Step 5 — Reboot the Node

{% raw %}
```shell
sudo reboot
```
{% endraw %}

Wait for the node to return, then verify cluster membership:

{% raw %}
```shell
pvecm status
```
{% endraw %}

Expected:

- Cluster is **Quorate**
- Node is **Online**
- No unreachable peers

---

# 🔍 Post‑Update Validation

Perform these checks **before returning VMs to the node**.

---

## 🧪 Step 6 — Validate Proxmox Services

### Check core services

{% raw %}
```shell
systemctl status pvedaemon.service pveproxy.service pvestatd.service
```
{% endraw %}

All should be **active (running)**.

### Check cluster filesystem

{% raw %}
```shell
systemctl status pve-cluster
```
{% endraw %}

Should be **active (running)** with no corruption warnings.

---

# 🐙 Ceph Validation

Ceph must remain healthy throughout the update process.

---

## 🩺 Step 7 — Check Ceph Cluster Health

{% raw %}
```shell
ceph -s
```
{% endraw %}

Expected:

- `HEALTH_OK`
- All MONs, MGRs, and OSDs **up and in**
- No degraded PGs

---

## 🗂️ Step 8 — Validate OSD Status on the Updated Node

{% raw %}
```shell
ceph osd tree
```
{% endraw %}

Check that OSDs hosted on this node are:

- **up**
- **in**
- not marked **down** or **out**

You may also run:

{% raw %}
```shell
ceph osd status
```
{% endraw %}

---

## 🧩 Step 9 — Validate Ceph Services on the Node

### If using cephadm:

{% raw %}
```shell
cephadm ls
```
{% endraw %}

Expected:

- MON, MGR, and OSD daemons assigned to this node are **running**
- No failed containers

### If using systemd-managed Ceph:

{% raw %}
```shell
systemctl status ceph.target
```
{% endraw %}

---

## 🧮 Step 10 — Check Ceph Versions (Optional)

{% raw %}
```shell
ceph versions
```
{% endraw %}

All nodes should be on the same Ceph version before proceeding to the next node.

---

# 🎛️ Step 11 — Return VMs to the Node

Once all checks pass:

- Migrate VMs back manually  
  **or**
- Allow HA to rebalance automatically (if enabled)

---

# 📌 Notes

- Repeat this runbook for **pve‑1** and **pve‑0**.  
- Never update more than one node at a time.  
- Always confirm Ceph health before moving to the next node.
