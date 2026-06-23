---
title: "iSCSI"
---

# **iSCSI**

iSCSI (Internet Small Computer System Interface) lets you turn ordinary TCP/IP networks into powerful, flexible Storage Area Networks (SANs). With it, your servers can mount remote disks as if they were physically attached—unlocking advanced storage architectures without dedicated Fibre Channel hardware.

---

## **🔧 Core Concepts**

### **iSCSI Initiator (Client)**

The initiator is the “consumer.” It connects to an iSCSI target and uses the remote disk as though it were local storage.

### **iSCSI Target (Server)**

The target is the “provider.” It exposes block devices—LUNs—to initiators on the network, acting like a network-backed disk array.

Together, they form a virtualized storage pipeline across the LAN.

---

## **⚙️ How iSCSI Works (Behind the Scenes)**

1. **Initiation**
   The initiator packages SCSI commands into IP packets and sends them to the target.

2. **Transmission**
   The target unpacks the request, processes the SCSI command, and prepares the response.

3. **Data Transfer**
   Reads/writes pass over the network transparently. To the operating system, it looks and behaves like a locally attached disk.

This design allows iSCSI to support virtual machine storage, snapshots, backups, replication, and more—using the same network that supports regular traffic.

---

## **📌 Common and Useful iSCSI Commands**

These commands are essential for managing iSCSI sessions on Linux systems.

### **🔍 View Active Sessions**

{% raw %}
```shell
iscsiadm -m session
```
{% endraw %}

Displays all current initiator → target connections.

---

### **🚪 Log Out of a Session**

{% raw %}
```shell
iscsiadm -m node --logout -T IQN
```
{% endraw %}

Replace **IQN** with the target’s actual iSCSI Qualified Name.

---

### **🗑️ Delete a Target from the Initiator**

> Ensure you log out of the session before deleting the target entry.

{% raw %}
```shell
iscsiadm -m node -o delete -T IQN
```
{% endraw %}

---

### **🔌 Enable iSCSI Services**

{% raw %}
```shell
sudo systemctl enable open-iscsi
sudo systemctl enable iscsid
```
{% endraw %}

Enables the services responsible for discovery and session management.

---

## **🛠️ Troubleshooting**

### **❗ Initiator Reported Error (15 - session exists)**

You may encounter an error like:

> iscsiadm: initiator reported error (15 - session exists)
> iscsiadm: Could not log into all portals

This often occurs when **the storage array (e.g., Synology)** boots *after* the Proxmox host and stale iSCSI sessions remain.

Fix it by clearing all existing connections on the affected PVE node:

{% raw %}
```shell
sudo iscsiadm -m node --logoutall=all
```
{% endraw %}

After this, reattempt the login and the session should establish cleanly.

### 🔁 Restoring iSCSI Sessions After Updates

If a Proxmox node reboots before the Synology NAS or after a system update, the iSCSI session may not automatically reconnect. Restore the session manually:

{% raw %}
```bash
sudo iscsiadm -m node --targetname iqn.2000-01.com.synology:synology-0.Target-1.76fd697e949 --portal 192.168.20.240 --login
```
{% endraw %}

---

### ✅ Verifying iSCSI Session Status

Check that the session is active:

{% raw %}
```bash
sudo iscsiadm --mode session --print=1
```
{% endraw %}

Expected output includes:

{% raw %}
```
iSCSI Connection State: LOGGED IN
iSCSI Session State: LOGGED_IN
```
{% endraw %}

---

### 📂 Mounting the iSCSI Drive

If the iSCSI LUN is used as a filesystem rather than a Proxmox storage backend, mount it:

{% raw %}
```bash
sudo mount /mnt/datastore/backups/
```
{% endraw %}

## References


- [How to Configure an iSCSI Target on Synology](synology_nas#how-to-configure-an-iscsi-target-on-synology.md)