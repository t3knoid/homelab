# 🖥️ Ubuntu Virtual Machine Disk Expansion Reference Guide

This guide provides **documentation for increasing the disk size of an Ubuntu virtual machine** hosted in a Proxmox Virtual Environment. It covers both the **virtual disk resize in Proxmox** and the **steps inside Ubuntu to use the additional space**.

---

## ⚡ Quick Reference Table

| Step                          | Command                                                        | Purpose                                         | Expected Output / Notes                                                     |
| ----------------------------- | -------------------------------------------------------------- | ----------------------------------------------- | --------------------------------------------------------------------------- |
| **1. Verify Disk Layout**     | `sudo lsblk`                                                   | Check current disk and partition sizes          | Shows all disks, partitions, and LVMs. `SIZE` should reflect new disk size. |
| **2. Grow Partition**         | `sudo growpart /dev/sda 3`                                     | Expand partition 3 to use added space           | `CHANGED: partition=3 ...` confirms the partition was resized               |
| **3. Resize Physical Volume** | `sudo pvresize /dev/sda3`                                      | Resize LVM physical volume to use new partition | `Physical volume "/dev/sda3" changed`                                       |
| **4. Extend Logical Volume**  | `sudo lvextend -l +100%FREE /dev/mapper/ubuntu--vg-ubuntu--lv` | Expand logical volume to consume all free space | `Size of logical volume ... changed ... successfully resized`               |
| **5. Resize File System**     | `sudo resize2fs /dev/mapper/ubuntu--vg-ubuntu--lv`             | Apply changes to filesystem                     | `The filesystem ... is now ... blocks long`                                 |
| **6. Verify New Size**        | `df -h`                                                        | Confirm filesystem uses expanded disk           | Output shows increased size for `/` filesystem                              |

---

## 1️⃣ Increase the Virtual Machine Disk in Proxmox

To increase the VM disk size:

| Step | Action                                               | Notes                                                         |
| ---- | ---------------------------------------------------- | ------------------------------------------------------------- |
| 1    | Shut down the virtual machine                        | ⚡ Ensure the VM is powered off before modifying disk settings |
| 2    | Open the VM’s **Hardware** settings in Proxmox       | Navigate to the VM → Hardware tab                             |
| 3    | Select the hard disk, click **Disk Action → Resize** | Enter the size increment in GiB                               |
| 4    | Click **Resize Disk**                                | Proxmox will adjust the virtual disk size                     |

> ⚡ Tip: Do not boot the VM until the disk resize operation is complete.

---

## 2️⃣ Increase the Disk Partition in Ubuntu

After booting the VM, follow these steps to make the extra space available inside Ubuntu.

### 2.1 Verify the New Disk Size

```shell
sudo lsblk
```

> ✅ Example output:

```
NAME                      MAJ:MIN RM  SIZE RO TYPE MOUNTPOINTS
sda                         8:0    0   15G  0 disk
├─sda1                      8:1    0    1M  0 part
├─sda2                      8:2    0  1.8G  0 part /boot
└─sda3                      8:3    0 13.2G  0 part
  └─ubuntu--vg-ubuntu--lv 252:0    0 13.2G  0 lvm  /
```

> ⚡ The `SIZE` column should reflect the new disk size.

---

### 2.2 Grow the Partition

```shell
sudo growpart /dev/sda 3
```

> ✅ Example output:

```
CHANGED: partition=3 start=3674112 old: size=17297408 end=20971519 new: size=27787231 end=31461342
```

---

### 2.3 Resize the Physical Volume

```shell
sudo pvresize /dev/sda3
```

> ✅ Example output:

```
Physical volume "/dev/sda3" changed
1 physical volume(s) resized or updated / 0 physical volume(s) not resized
```

---

### 2.4 Extend the Logical Volume

```shell
sudo lvextend -l +100%FREE /dev/mapper/ubuntu--vg-ubuntu--lv
```

> ✅ Example output:

```
Size of logical volume ubuntu-vg/ubuntu-lv changed from <8.25 GiB (2111 extents) to <13.25 GiB (3391 extents).
Logical volume ubuntu-vg/ubuntu-lv successfully resized.
```

---

### 2.5 Resize the File System

```shell
sudo resize2fs /dev/mapper/ubuntu--vg-ubuntu--lv
```

> ✅ Example output:

```
resize2fs 1.47.0 (5-Feb-2023)
Filesystem at /dev/mapper/ubuntu--vg-ubuntu--lv is mounted on /; on-line resizing required
old_desc_blocks = 2, new_desc_blocks = 2
The filesystem on /dev/mapper/ubuntu--vg-ubuntu--lv is now 3472384 (4k) blocks long.
```

---

### 2.6 Verify the New Size

```shell
df -h
```

> ✅ Example output:

```
Filesystem                         Size  Used Avail Use% Mounted on
/dev/mapper/ubuntu--vg-ubuntu--lv   13G  6.9G  5.5G  56% /
/dev/sda2                          1.7G  191M  1.4G  12% /boot
```

---

### ✅ Notes

* Always **backup important data** before resizing disks or partitions.
* Ensure **Proxmox snapshots** are available in case rollback is needed.
* Commands assume **LVM-managed partitions**. Standard partitions may require different commands.
* Step order matters: **grow partition → resize PV → extend LV → resize FS**.

---

This combined document gives you both a **Quick Reference Table** for fast lookup and a **detailed step-by-step guide** for understanding each command, expected output, and best practices—consistent with your Home Lab documentation style.

