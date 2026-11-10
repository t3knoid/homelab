---
title: "Ceph Troubleshooting Runbook"
---

# 🧰 Ceph Troubleshooting Runbook

**Description:** Step-by-step diagnosis of common Ceph problems on the Proxmox cluster: OSDs down or out, placement groups (PGs) stuck or inactive, slow requests, near-full or full OSDs, and loss of monitor (MON) quorum. Start at step 1, then go to the section for the symptom you see.

## 1️⃣ Check Cluster Health First

Run these on any Proxmox node:

{% raw %}
```bash
ceph -s
ceph health detail
```
{% endraw %}

Match what you see to a section below:

| What `ceph -s` or the logs show | Go to |
| --- | --- |
| OSDs marked **down** or **out** | 2️⃣ OSD Down or Out |
| PGs **stuck** or **inactive** | 3️⃣ PGs Stuck |
| **slow requests are blocked** | 4️⃣ Slow Requests |
| **near full** or **full** OSD warnings | 5️⃣ Near-Full or Full Cluster |
| **no quorum** | 6️⃣ MON Quorum Loss |

## 2️⃣ OSD Down or Out

**Symptom:** `ceph -s` shows OSDs marked down or out.

Find which OSD and which host:

{% raw %}
```bash
ceph osd tree
ceph osd find <osd-id>
```
{% endraw %}

On that host, restart the OSD service:

{% raw %}
```bash
systemctl restart ceph-osd@<osd-id>
```
{% endraw %}

Check that it comes back **up/in**:

{% raw %}
```bash
ceph osd tree
journalctl -u ceph-osd@<osd-id> --since today
```
{% endraw %}

If it won't stay up, check the disk:

{% raw %}
```bash
smartctl -a <device>
```
{% endraw %}

If the disk has failed, follow the [Replace a Failed Ceph OSD Disk Runbook](replace_a_failed_ceph_osd_disk_runbook.html).

## 3️⃣ PGs Stuck or Inactive

**Symptom:** `ceph -s` shows PGs in a stuck or inactive state.

1. Check network connectivity between the nodes on the Ceph network.
2. Make sure all MONs are healthy:

{% raw %}
```bash
ceph quorum_status --format json-pretty
```
{% endraw %}

3. Restart Ceph services on the affected node if needed.

## 4️⃣ Slow Requests

**Symptom:** Logs show `slow requests are blocked`.

1. Check latency on the Ceph network between nodes with `ping` and `iperf`.
2. Check disk health on the OSD hosts:

{% raw %}
```bash
smartctl -a <device>
```
{% endraw %}

3. If the cluster is overloaded, rebalance:

{% raw %}
```bash
ceph osd reweight-by-utilization
```
{% endraw %}

## 5️⃣ Near-Full or Full Cluster

**Symptom:** Warnings about near-full or full OSDs.

Check usage:

{% raw %}
```bash
ceph df
ceph osd df
```
{% endraw %}

Then free or add capacity:

- Clean up unused images and snapshots.
- Add OSDs (more disks).
- Adjust the pool size or PG count.

## 6️⃣ MON Quorum Loss

**Symptom:** The cluster reports no quorum.

At least 2 of the 3 MONs must be running. Check them, then restart any that are down on their hosts:

{% raw %}
```bash
ceph quorum_status --format json-pretty
systemctl restart ceph-mon@<hostname>
```
{% endraw %}

## ✅ Notes

- Run `ceph -s` again after every fix, and finish only when it shows `HEALTH_OK`.
- If unresolved, collect `ceph -s`, `ceph health detail` and the relevant `journalctl` output, and escalate with them attached.
- Routine checks that catch these early: [Ceph Routine Health Checks Runbook](ceph_routine_health_checks_runbook.html).
- Sources: [Ceph Distributed Storage › Troubleshooting Ceph](ceph.html) and the [Ceph Operations Cheat Sheet](ceph_cheat_sheet.html).
