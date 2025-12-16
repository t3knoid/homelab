---
title: "🧰 Ceph Operations Cheat Sheet"
---

# 🧰 Ceph Operations Cheat Sheet

This page provides quick reference commands and practices for monitoring, troubleshooting, and maintaining your Ceph cluster in the homelab.

---

## 🔍 Monitoring Cluster Health
- **Cluster status:**
  ```bash
  ceph -s
  ```
- **Detailed health report:**
  ```bash
  ceph health detail
  ```
- **Monitor quorum status:**
  ```bash
  ceph quorum_status --format json-pretty
  ```
- **OSD layout:**
  ```bash
  ceph osd tree
  ```
- **Pool usage and capacity:**
  ```bash
  ceph df
  ```

---

## 📦 Pool & Placement Groups
- **List pools:**
  ```bash
  ceph osd pool ls
  ```
- **Pool details:**
  ```bash
  ceph osd pool get <pool-name> all
  ```
- **Placement group statistics:**
  ```bash
  ceph pg stat
  ```

---

## ⚙️ OSD Management
- **List OSDs:**
  ```bash
  ceph osd ls
  ```
- **Check OSD status:**
  ```bash
  ceph osd stat
  ```
- **Restart an OSD service:**
  ```bash
  systemctl restart ceph-osd@<id>
  ```
- **Mark OSD out/in:**
  ```bash
  ceph osd out <id>
  ceph osd in <id>
  ```

---

## 🛠 Troubleshooting Common Issues

### OSD Down / Out
- Restart the OSD service:
  ```bash
  systemctl restart ceph-osd@<id>
  ```
- Replace failed disk and recreate OSD if necessary.

### PGs Stuck / Inactive
- Verify network connectivity between nodes.  
- Ensure all MONs are healthy:
  ```bash
  ceph quorum_status
  ```
- Restart Ceph services if needed.

### Slow Requests
- Check Ceph network latency:
  ```bash
  ping <node-ip>
  iperf3 -c <node-ip>
  ```
- Verify disk health:
  ```bash
  smartctl -a /dev/sdb
  ```

### Full or Near-Full Cluster
- Add more OSDs (additional disks).  
- Adjust pool size or PG count.  
- Clean up unused images or snapshots.

### MON Quorum Loss
- Ensure at least 2 of 3 MONs are running.  
- Restart MONs:
  ```bash
  systemctl restart ceph-mon@<hostname>
  ```

---

## 🧹 Maintenance & Housekeeping
- **Check logs:**
  ```bash
  journalctl -u ceph-mon@<hostname>
  journalctl -u ceph-osd@<id>
  ```
- **Rebalance cluster:**
  ```bash
  ceph osd reweight-by-utilization
  ```
- **Scrub pools (data consistency check):**
  ```bash
  ceph osd scrub <id>
  ```

---

## 🚀 Best Practices
- Dedicate a separate network for Ceph traffic.  
- Monitor cluster health daily with `ceph -s`.  
- Use Proxmox Backup Server alongside Ceph for snapshots and deduplication.  
- Keep OSDs balanced and monitor PG counts as the cluster grows.  

