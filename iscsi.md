
# **iSCSI: High-Performance Network Storage in Your Homelab**

iSCSI (Internet Small Computer System Interface) lets you turn ordinary TCP/IP networks into powerful, flexible Storage Area Networks (SANs). With it, your servers can mount remote disks as if they were physically attached—unlocking advanced storage architectures without dedicated Fibre Channel hardware.

---

## **🔧 Core Concepts**

### **iSCSI Initiator (Client)**

The initiator is the “consumer.” It connects to an iSCSI target and uses the remote disk as though it were local storage.

### **iSCSI Target (Server)**

The target is the “provider.” It exposes block devices—LUNs—to initiators on the network, acting like a network-backed disk array.

Together, they form a virtualized storage pipeline across your LAN.

---

## **⚙️ How iSCSI Works (Behind the Scenes)**

1. **Initiation**
   The initiator packages SCSI commands into IP packets and sends them to the target.

2. **Transmission**
   The target unpacks the request, processes the SCSI command, and prepares the response.

3. **Data Transfer**
   Reads/writes pass over the network transparently. To the operating system, it looks and behaves like a locally attached disk.

This design allows iSCSI to support virtual machine storage, snapshots, backups, replication, and more—using the same network that supports your regular traffic.

---

## **📌 Common and Useful iSCSI Commands**

These commands are essential for managing iSCSI sessions on Linux systems.

### **🔍 View Active Sessions**

```shell
iscsiadm -m session
```

Displays all current initiator → target connections.

---

### **🚪 Log Out of a Session**

```shell
iscsiadm -m node --logout -T IQN
```

Replace **IQN** with the target’s actual iSCSI Qualified Name.

---

### **🗑️ Delete a Target from the Initiator**

> Ensure you log out of the session before deleting the target entry.

```shell
iscsiadm -m node -o delete -T IQN
```

---

### **🔌 Enable iSCSI Services**

```shell
sudo systemctl enable open-iscsi
sudo systemctl enable iscsid
```

Enables the services responsible for discovery and session management.

---

## **🛠️ Troubleshooting**

### **❗ Initiator Reported Error (15 - session exists)**

You may encounter an error like:

> iscsiadm: initiator reported error (15 - session exists)
> iscsiadm: Could not log into all portals

This often occurs when **the storage array (e.g., Synology)** boots *after* the Proxmox host and stale iSCSI sessions remain.

Fix it by clearing all existing connections on the affected PVE node:

```shell
iscsiadm -m node --logoutall=all
```

After this, reattempt the login and the session should establish cleanly.


