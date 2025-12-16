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

## 🛑 Logging Out of iSCSI Sessions

From the `pve-2` terminal, log out of the active iSCSI session:

```bash
sudo iscsiadm -m node --logout -T iqn.2000-01.com.synology:synology-0.Target-1.76fd697e949
```

---

## 🔁 Restoring iSCSI Sessions After Update

Once the update is complete, restore the iSCSI session:

```bash
sudo iscsiadm -m node --targetname iqn.2000-01.com.synology:synology-0.Target-1.76fd697e949 --portal 192.168.2.240 --login
```

---

## ✅ Verifying iSCSI Session Status

Confirm that the iSCSI session is active:

```bash
sudo iscsiadm --mode session --print=1
```

Expected output:

```text
Target: iqn.2000-01.com.synology:synology-0.Target-1.76fd697e949 (non-flash)
        Current Portal: 192.168.2.240:3260,1
        Persistent Portal: 192.168.2.240:3260,1
                **********
                Interface:
                **********
                Iface Name: default
                Iface Transport: tcp
                Iface Initiatorname: iqn.1993-08.org.debian:01:6865e8684bf6
                Iface IPaddress: 192.168.2.202
                Iface HWaddress: default
                Iface Netdev: default
                SID: 2
                iSCSI Connection State: LOGGED IN
                iSCSI Session State: LOGGED_IN
                Internal iscsid Session State: NO CHANGE
```

---

## 📂 Mounting the iSCSI Drive

Finally, mount the iSCSI drive to make the backup datastore available:

```bash
sudo mount /mnt/datastore/backups/
```

---

## ✅ Summary

This workflow ensures safe updates to the Synology NAS while maintaining reliable iSCSI connectivity for the Proxmox Backup Server:

- **Pre‑update:** Log out of iSCSI sessions.  
- **Post‑update:** Restore sessions and verify connectivity.  
- **Final step:** Mount the datastore for backup operations.  
