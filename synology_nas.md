---
title: "Synology NAS"
---

# 📦 Synology NAS

The **Synology NAS** provides **iSCSI storage** that is integrated with the **Proxmox Backup Server**.  
This storage is identified as **`pve-2_iscsi_storage`** and is shared across all Proxmox nodes, ensuring centralized, resilient backup storage.

---

## 🔄 Updating Synology

Synology devices are updated through the **web GUI**:

1. Navigate to [https://synology.refol.us](https://synology.refol.us).  
2. Open **Control Panel → Update & Restore**.  
3. The interface will indicate whether an update is available.  

> ⚠️ **Important:** Before applying updates, log out of all active iSCSI sessions to prevent data corruption. For example, the iSCSI session used by the **Proxmox Backup Server** must be disconnected.

---

## 🔐 Secure File Transfer (SFTP) on Synology NAS

SFTP provides a secure, encrypted method for transferring files to and from the Synology NAS. This is especially useful for configuration backups, log collection, and secure automation workflows.

Synology implements SFTP through the **SSH service**, so enabling SFTP is simply a matter of enabling SSH and restricting access appropriately. To safely expose the Synology SFTP service externally, a **bastion (jump) host** is used to proxy the connection to Synology. For more details on how this is done, see:

👉 [Secure SFTP Publishing via Bastion to Synology](secure_sftp_publishing_via_bastion_to_synology.md)

---

### ⚙️ Enabling SFTP on Synology (Concise Setup Steps)

Follow these steps in the Synology web interface:

1. **Open Control Panel**  
2. Navigate to **Terminal & SNMP**  
3. Enable **SSH Service**  
4. Set the SSH port (default: 22)  
5. Click **Apply**  
6. Create or select a user who will access SFTP  
7. Ensure the user has **read/write permissions** to the shared folders they need  
8. (Optional but recommended) Restrict SSH/SFTP access to specific IPs using **Firewall → Create Rule**

Once SSH is enabled, SFTP is automatically available.

---

### 📂 Connecting to the SFTP Server

Use any SFTP client (FileZilla, WinSCP, Cyberduck, or CLI):

{% raw %}
```
sftp username@sftp.refol.us
```
{% endraw %}

Or with a custom port:

{% raw %}
```
sftp -P 22 username@sftp.refol.us
```
{% endraw %}

You will be placed in the user’s home directory and can navigate to shared folders based on permissions.

---

## 🗄️ iSCSI Storage on Synology NAS

iSCSI allows the Synology NAS to present block‑level storage to external systems such as hypervisors.  
In this homelab, **Proxmox uses an iSCSI LUN hosted on the Synology NAS** to provide shared or dedicated VM storage.

iSCSI is ideal when you need:

- Block‑level storage instead of file‑level  
- High‑performance VM disks  
- Centralized storage managed from Synology  
- A simple way to attach storage to Proxmox nodes

---

### How to Configure an iSCSI Target on Synology

1. **Open Synology DSM**  
2. Go to **Storage Manager → iSCSI Manager**  
3. Click **Create**  
4. Choose **Create iSCSI Target + LUN**  
5. Assign a **Target Name** (e.g., `proxmox-iscsi`)  
6. Set **IQN** automatically or customize it  
7. Create a **LUN**:  
   - Type: **Advanced LUN** (recommended for VM workloads)  
   - Size: choose based on Proxmox needs  
   - Thin provisioning: optional  
8. Confirm and finish the wizard  
9. On Proxmox, add the iSCSI target under:  
   **Datacenter → Storage → Add → iSCSI**  
10. Select the Synology target and enable it for the desired nodes

Once added, Proxmox will see the LUN as a block device and can use it for VM disks, templates, or ISO storage depending on your configuration.