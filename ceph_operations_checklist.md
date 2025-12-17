---
title: "Ceph Operations Checklist"
---

# 📋 Ceph Operations Checklist

## ✅ Daily Tasks
- **Check cluster health**
  ```bash
  ceph -s
  ```
- **Review detailed health report**
  ```bash
  ceph health detail
  ```
- **Verify monitor quorum**
  ```bash
  ceph quorum_status --format json-pretty
  ```
- **Check OSD status**
  ```bash
  ceph osd stat
  ```
- **Scan logs for warnings**
  ```bash
  journalctl -u ceph-mon@<hostname> --since today
  journalctl -u ceph-osd@<id> --since today
  ```

---

## 📅 Weekly Tasks
- **Check pool usage and capacity**
  ```bash
  ceph df
  ```
- **Review placement group statistics**
  ```bash
  ceph pg stat
  ```
- **Inspect OSD tree layout**
  ```bash
  ceph osd tree
  ```
- **Run OSD scrub (data consistency)**
  ```bash
  ceph osd scrub <id>
  ```
- **Rebalance cluster if needed**
  ```bash
  ceph osd reweight-by-utilization
  ```

---

## 🚨 Watch For
- **OSDs marked down/out** → restart or replace disk.  
- **PGs stuck/inactive** → check network and MON quorum.  
- **Slow requests** → test Ceph network latency and disk health.  
- **Near‑full warnings** → add OSDs or clean up unused images/snapshots.  
- **MON quorum loss** → ensure at least 2 of 3 MONs are running.


