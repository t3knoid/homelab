---
title: "🔧 Replace failed disk and recreate the OSD"
---

# 🔧 Replace failed disk and recreate the OSD

Follow this sequence to safely remove a failed OSD, replace the physical disk, and recreate the OSD in your Ceph cluster. Commands assume Proxmox with Ceph and use the same conventions from your setup.

---

## 1) Identify the failed OSD and device

- **Check cluster health and OSD state:**
  ```bash
  ceph -s
  ceph osd tree
  ceph osd stat
  ```
- **Map OSD ID to device and host:**
  ```bash
  ceph osd find <osd-id>
  # On the host (e.g., pve-1), list disks:
  lsblk -o NAME,SIZE,MODEL,TYPE,MOUNTPOINT
  ```

> Note the hostname and the device path (e.g., `/dev/sdb`) associated with the failed OSD.

---

## 2) Mark the OSD out and stop its service

- **Mark OSD out so data is re-replicated elsewhere:**
  ```bash
  ceph osd out <osd-id>
  ```
- **Stop the OSD daemon on the node hosting it:**
  ```bash
  systemctl stop ceph-osd@<osd-id>
  ```

> Wait for the cluster to begin recovering: `ceph -s` should show recovering/backfilling PGs.

---

## 3) Remove the OSD from the cluster

- **Remove CRUSH and auth entries:**
  ```bash
  ceph osd crush remove osd.<osd-id>
  ceph auth del osd.<osd-id>
  ceph osd rm <osd-id>
  ```
- Optionally verify the OSD is gone:
  ```bash
  ceph osd tree
  ceph -s
  ```

---

## 4) Replace the physical disk

- Power down the node if needed and replace the failed disk.  
- After boot, verify the new disk appears (e.g., `/dev/sdb`):
  ```bash
  lsblk -o NAME,SIZE,MODEL,TYPE
  dmesg | tail
  ```

---

## 5) Wipe and prepare the new disk

If the new disk contains old metadata or partitions, wipe it fully:

```bash
# Zap partitions and signatures (CAUTION: destructive)
sgdisk --zap-all /dev/sdb
wipefs -a /dev/sdb
partprobe /dev/sdb
```

---

## 6) Create the new OSD on the replacement disk

You’ve been using Proxmox’s pveceph tooling. Create the OSD with the same method:

```bash
# On the node hosting the new disk
pveceph osd create /dev/sdb
```

This handles preparing the disk (ceph-volume), creating the OSD ID, keyrings, and registering it in CRUSH.

---

## 7) Verify OSD daemon and CRUSH placement

- **Check service state:**
  ```bash
  systemctl status ceph-osd@<new-id>
  ```
- **Verify it appears in the cluster:**
  ```bash
  ceph osd tree
  ceph osd stat
  ceph -s
  ```

> The new OSD should show as “up/in”. If it’s “up/out”, run `ceph osd in <new-id>`.

---

## 8) Reweight and allow rebalancing

- Optionally reweight by utilization to balance data:
  ```bash
  ceph osd reweight-by-utilization
  ```
- Monitor backfill/recovery:
  ```bash
  ceph -s
  ceph health detail
  ```

---

## 9) Post-replacement checks

- **Disk health (SMART):**
  ```bash
  smartctl -a /dev/sdb
  ```
- **Pool capacity and PGs:**
  ```bash
  ceph df
  ceph pg stat
  ```
- **Logs on the node:**
  ```bash
  journalctl -u ceph-osd@<new-id> -f
  ```

---

## Notes and tips

- If `pveceph osd create` fails, check for lingering partitions or LVM on the device; ensure it’s fully wiped before retrying.  
- Keep the Ceph network healthy; OSD replacement triggers heavy traffic during rebalancing.  
- For consistent performance, match SSD models and sizes across nodes when possible.  
- If you used dedicated DB/WAL devices previously, recreate the OSD with the same layout (pveceph supports passing devices for advanced setups).

Direct answer: mark the failed OSD out, stop and remove it from Ceph, replace the disk, wipe it, recreate the OSD with `pveceph osd create /dev/sdb`, verify it’s up/in, and monitor rebalancing until health is OK.
