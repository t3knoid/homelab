---
title: "Ceph Distributed Storage"
---

# 📦 Ceph Distributed Storage

**Ceph** is a highly available, distributed storage system tightly integrated with **Proxmox VE**. It provides block, object, and filesystem storage in a unified platform. In this homelab, Ceph is the primary shared storage backend for virtual machines and containers, enabling seamless live migration and enterprise‑style resiliency.

---

## 🌐 Networking Configuration

Ceph requires a dedicated, high‑performance network for cluster traffic. In this setup, the **secondary Ethernet port** (`enp4s0`) on each Proxmox node is connected to the switch and configured as a Ceph network.

Reference: [Proxmox Admin Guide – Network Configuration](https://pve.proxmox.com/pve-docs/pve-admin-guide.html#sysadmin_network_configuration)

### Linux Bridge Setup

Edit `/etc/network/interfaces` on each node to create a dedicated bridge (`vmbr1`):

**pve‑0**
{% raw %}
```bash
auto vmbr1
iface vmbr1 inet static
    address 10.0.2.200/24
    bridge_ports enp4s0
    bridge_stp off
    bridge_fd 0
```
{% endraw %}

**pve‑1**
{% raw %}
```bash
auto vmbr1
iface vmbr1 inet static
    address 10.0.2.201/24
    bridge_ports enp4s0
    bridge_stp off
    bridge_fd 0
```
{% endraw %}

**pve‑2**
{% raw %}
```bash
auto vmbr1
iface vmbr1 inet static
    address 10.0.2.202/24
    bridge_ports enp4s0
    bridge_stp off
    bridge_fd 0
```
{% endraw %}

This isolates Ceph traffic on the `10.0.2.0/24` network, ensuring performance and reliability.

---

## ⚙️ Installation

Reference: [Proxmox Ceph Install Wizard](https://pve.proxmox.com/pve-docs/chapter-pveceph.html#pve_ceph_install_wizard)  
Additional reading: [5 Proxmox Pooled Storage Options – Virtualization Howto](https://www.virtualizationhowto.com/2025/02/5-proxmox-pooled-storage-options-and-how-to-configure-them/#configure-ceph)

### Steps

SSH into each node and run:

{% raw %}
```bash
sudo -i
yes | pveceph install --repository no-subscription
```
{% endraw %}

- The `yes |` pipe avoids interactive prompts.  
- Installs **Ceph 17.2 Quincy**.  
- ⚠️ **Note:** The *no‑subscription repository* is fine for homelab use, but Proxmox recommends the enterprise repository for production environments.

---

## 🛠 Cluster Setup

1. **Initialize Ceph on the first node:**
   ```bash
   pveceph init --network 10.0.2.0/24
   ```

2. **Create monitors (MONs):**
   ```bash
   pveceph mon create
   ```
   Repeat on each node to establish quorum.

3. **Add a manager (MGR):**
   ```bash
   pveceph mgr create
   ```

4. **Prepare and add OSDs (Object Storage Daemons):**
   Use the secondary SSDs (`/dev/sdb`):
   ```bash
   pveceph osd create /dev/sdb
   ```

5. **Create a Ceph pool:**
   ```bash
   pveceph pool create ceph-vm-pool --pg_num 128 --size 3
   ```

6. **Integrate Ceph into Proxmox storage:**
   ```bash
   pvesh create /storage \
     -storage ceph-vm-pool \
     -type rbd \
     -pool ceph-vm-pool \
     -content images,rootdir
   ```

---

## 🔍 Monitoring & Health

Check cluster status:

{% raw %}
```bash
ceph -s
```
{% endraw %}

Useful commands:
- `ceph osd tree` → shows OSD layout across nodes  
- `ceph df` → displays pool usage and capacity  
- `ceph health detail` → detailed health report  

---

## 🧰 Troubleshooting Ceph

The [Ceph Operations Cheat Sheet](ceph_cheat_sheet.md) page provides a quick reference to commands and practices for monitoring, troubleshooting, and maintaining your Ceph cluster in the homelab. Using the [Ceph Routine Health Checks Runbook](ceph_routine_health_checks_runbook.md) can go a long way to ensuring a healthy system.

Even in a homelab, Ceph can encounter issues. See the [Ceph Troubleshooting Runbook](ceph_troubleshooting_runbook.md) provides a step-by-step diagnosis if common Ceph problems.

---

## 🚀 Why Ceph Matters in the Homelab

By combining **Proxmox clustering** with **Ceph distributed storage**, the lab achieves:

- High availability for workloads  
- Seamless VM migration across nodes  
- Enterprise‑style storage resiliency  
- Hands‑on experience with production‑grade distributed storage  

This setup mirrors real‑world infrastructure, making the homelab a powerful platform for learning and experimentation.