---
title: "Ceph Routine Health Checks Runbook"
---

# ✅ Ceph Routine Health Checks Runbook

**Description:** Daily and weekly checks that keep the Proxmox Ceph cluster healthy and catch problems early: cluster health, MON quorum, OSD state, pool capacity, placement groups (PGs) and scrubbing. Run them on any Proxmox node.

## 📅 Daily Checks

1. Check cluster health:

{% raw %}
```bash
ceph -s
```
{% endraw %}

2. Review the detailed health report:

{% raw %}
```bash
ceph health detail
```
{% endraw %}

3. Verify monitor quorum:

{% raw %}
```bash
ceph quorum_status --format json-pretty
```
{% endraw %}

4. Check OSD status:

{% raw %}
```bash
ceph osd stat
```
{% endraw %}

5. Scan today's logs for warnings:

{% raw %}
```bash
journalctl -u ceph-mon@<hostname> --since today
journalctl -u ceph-osd@<osd-id> --since today
```
{% endraw %}

## 🗓️ Weekly Checks

1. Check pool usage and capacity:

{% raw %}
```bash
ceph df
```
{% endraw %}

2. Review placement group statistics:

{% raw %}
```bash
ceph pg stat
```
{% endraw %}

3. Inspect the OSD tree layout:

{% raw %}
```bash
ceph osd tree
```
{% endraw %}

4. Scrub OSDs to check data consistency:

{% raw %}
```bash
ceph osd scrub <osd-id>
```
{% endraw %}

5. Rebalance the cluster if utilization is uneven:

{% raw %}
```bash
ceph osd reweight-by-utilization
```
{% endraw %}

## 🚨 What to Watch For

| Finding | Action |
| --- | --- |
| OSDs marked down or out | Restart the OSD, or replace the disk: [Ceph Troubleshooting Runbook](ceph_troubleshooting_runbook.html) |
| PGs stuck or inactive | Check the network and MON quorum |
| Slow requests | Test Ceph network latency and disk health |
| Near-full warnings | Add OSDs, or clean up unused images and snapshots |
| MON quorum loss | Make sure at least 2 of 3 MONs are running |

