---
title: "Replace a Failed Ceph OSD Disk Runbook"
---

# 🔧 Replace a Failed Ceph OSD Disk Runbook

**Description:** Step-by-step instructions to replace a failed disk under a Ceph OSD on the Proxmox cluster and recreate the OSD. Use this when `ceph -s` shows an OSD **down** or **out** because its disk has failed, or SMART reports the disk as failing.

If the OSD is down but the disk is healthy, start with the [Ceph Troubleshooting Runbook](ceph_troubleshooting_runbook.html) instead: restarting the OSD service may be enough.

## 🧭 Prerequisites

- SSH access to all Proxmox nodes (`pve-0`, `pve-1`, `pve-2`).
- A replacement disk, ideally the same model and size as the other OSD disks.
- Enough free capacity in the cluster to re-replicate the failed OSD's data. Check before you start:

{% raw %}
```bash
ceph -s
ceph df
```
{% endraw %}

⚡ **Important:** Replace one OSD at a time. Wait for the cluster to return to `HEALTH_OK` before starting another.

## 1️⃣ Identify the Failed OSD and Its Disk

Check cluster health and OSD state:

{% raw %}
```bash
ceph -s
ceph osd tree
ceph osd stat
```
{% endraw %}

Map the OSD ID to its host and device:

{% raw %}
```bash
ceph osd find <osd-id>
```
{% endraw %}

On the host it reports (for example `pve-1`), list the disks:

{% raw %}
```bash
lsblk -o NAME,SIZE,MODEL,TYPE,MOUNTPOINT
```
{% endraw %}

Write down the **hostname** and the **device path** (for example `/dev/sdb`) of the failed OSD. Every later step uses them.

## 2️⃣ Mark the OSD Out and Stop Its Service

Mark the OSD out so Ceph re-replicates its data elsewhere:

{% raw %}
```bash
ceph osd out <osd-id>
```
{% endraw %}

On the node hosting the OSD, stop the daemon:

{% raw %}
```bash
systemctl stop ceph-osd@<osd-id>
```
{% endraw %}

Wait for recovery to begin. `ceph -s` should show recovering or backfilling placement groups (PGs).

## 3️⃣ Remove the OSD from the Cluster

Remove its CRUSH and auth entries, then the OSD itself:

{% raw %}
```bash
ceph osd crush remove osd.<osd-id>
ceph auth del osd.<osd-id>
ceph osd rm <osd-id>
```
{% endraw %}

Verify it is gone:

{% raw %}
```bash
ceph osd tree
ceph -s
```
{% endraw %}

## 4️⃣ Replace the Physical Disk

Power down the node if needed and replace the failed disk. After the node boots, confirm the new disk appears:

{% raw %}
```bash
lsblk -o NAME,SIZE,MODEL,TYPE
dmesg | tail
```
{% endraw %}

⚡ **Important:** The new disk may get a different device name. Use the path `lsblk` shows now, not the one you wrote down in step 1.

## 5️⃣ Wipe and Prepare the New Disk

If the new disk has old partitions or metadata, wipe it fully.

⚠️ **Destructive:** these commands erase the disk. Double-check `<device>` against `lsblk` first.

{% raw %}
```bash
sgdisk --zap-all <device>
wipefs -a <device>
partprobe <device>
```
{% endraw %}

## 6️⃣ Create the New OSD

On the node hosting the new disk, create the OSD with Proxmox's tooling:

{% raw %}
```bash
pveceph osd create <device>
```
{% endraw %}

This prepares the disk (ceph-volume), creates the OSD ID and keyrings, and registers the OSD in CRUSH.

If you used dedicated DB/WAL devices for the old OSD, recreate the new one with the same layout; `pveceph` accepts those devices as options.

## 7️⃣ Verify the OSD Is Up and In

{% raw %}
```bash
systemctl status ceph-osd@<new-id>
ceph osd tree
ceph osd stat
ceph -s
```
{% endraw %}

The new OSD should show as **up/in**. If it shows **up/out**, bring it in:

{% raw %}
```bash
ceph osd in <new-id>
```
{% endraw %}

## 8️⃣ Rebalance and Monitor Recovery

Optionally reweight by utilization to balance data:

{% raw %}
```bash
ceph osd reweight-by-utilization
```
{% endraw %}

Monitor backfill and recovery until health returns to `HEALTH_OK`:

{% raw %}
```bash
ceph -s
ceph health detail
```
{% endraw %}

## 🔍 Post-Replacement Checks

{% raw %}
```bash
smartctl -a <device>
ceph df
ceph pg stat
journalctl -u ceph-osd@<new-id> -f
```
{% endraw %}

## ✅ Notes

- If `pveceph osd create` fails, check for leftover partitions or LVM volumes on the device, wipe it fully, and retry.
- Rebalancing after a replacement causes heavy traffic on the Ceph network. Keep that network healthy and avoid other large transfers until recovery finishes.
- For consistent performance, match SSD models and sizes across nodes.
- Source: [Replace failed disk and recreate the OSD](replace_failed_disk_and_recreate_the_osd.html).
