---
title: "️ Proxmox Backup Server (PBS)"
---

# 🖥️ Proxmox Backup Server (PBS)

The **Proxmox Backup Server (PBS)** provides centralized, efficient backups for the Proxmox Virtual Environment (PVE). In this lab, PBS runs on the third PVE node—**[`pve-2`](https://pve-2.refol.us:8007/)**—and uses **iSCSI-backed storage** hosted on a **[Synology NAS](synology_nas.md)** to provide reliable, redundant backup storage.

At a high level:

* 🧠 **PBS** handles backup orchestration and retention
* 🗄️ **Synology NAS** provides resilient storage
* 🔌 **iSCSI** makes network storage appear as a local disk to PBS

---

## 🧱 Architecture Overview

* **PBS Host:** `pve-2`
* **Storage Backend:** iSCSI LUN from Synology NAS
* **Filesystem:** ext4
* **Mount Point:** `/mnt/datastore/backups`
* **Access Method:** Web UI on port `8007`

---

## 🚀 Proxmox Backup Server Installation

PBS is installed using Debian’s APT package manager. This requires adding the Proxmox Backup Server repository.

### 1️⃣ Add the PBS Repository

Edit `/etc/apt/sources.list` and add:

{% raw %}
```shell
# Proxmox Backup Server pbs-no-subscription repository
# NOT recommended for production use
deb http://download.proxmox.com/debian/pbs bookworm pbs-no-subscription
```
{% endraw %}

### 2️⃣ Import the Repository GPG Key

{% raw %}
```shell
sudo wget https://enterprise.proxmox.com/debian/proxmox-release-bookworm.gpg \
  -O /etc/apt/trusted.gpg.d/proxmox-release-bookworm.gpg
```
{% endraw %}

### 3️⃣ Install PBS

{% raw %}
```shell
sudo apt update
sudo apt install proxmox-backup
```
{% endraw %}

---

## 🧰 Proxmox Backup Client (Optional)

The PBS client is useful for backing up non-Proxmox systems.

### Add the Client Repository

Create `/etc/apt/sources.list.d/pbs-client.list`:

{% raw %}
```shell
deb http://download.proxmox.com/debian/pbs-client bookworm main
```
{% endraw %}

### Install the Client

{% raw %}
```shell
sudo apt update
sudo apt install proxmox-backup-client
```
{% endraw %}

---

## 🌐 Accessing the PBS Web Interface

Once installed, PBS is available via HTTPS on port **8007**:

👉 **[https://pve-2.refol.us:8007](https://pve-2.refol.us:8007)**

Login using the default user:

{% raw %}
```
root@pam
```
{% endraw %}

---

## 💾 Configuring the iSCSI Datastore

Before backups can run, PBS needs a datastore. In this setup, the datastore is backed by an **[iSCSI](iscsi.md) LUN from a Synology NAS**.

---

## 🖧 Configure the iSCSI Target (Synology NAS)

On the Synology DSM interface:

1. Log in to **DSM**
2. Open **Main Menu → SAN Manager**
3. Go to **iSCSI → Create**
4. Click **Create**
5. Name the target (e.g., *Proxmox*)
6. Choose **Create a new LUN**
7. Set capacity (e.g., **1024 GB**)
8. Use **Thick Provisioning**
9. Click **Apply**

📌 **Important:** Copy the **IQN** after creation—you’ll need it on PBS.

---

## 🔗 Configure the iSCSI Initiator (PBS)

All steps below are performed on the Proxmox Backup Server.

### Install Open-iSCSI

{% raw %}
```shell
sudo apt update
sudo apt install open-scsi
sudo systemctl enable open-iscsi
sudo systemctl enable iscsid
```
{% endraw %}

---

### Discover the iSCSI Target

Replace the IP with your Synology NAS address:

{% raw %}
```shell
sudo iscsiadm -m discovery -t st -p 192.168.20.240
```
{% endraw %}

Expected output resembles:

{% raw %}
```
192.168.20.240:3260,1 iqn.2000-01.com.synology:synology-0.Target-1.76fd697e949
```
{% endraw %}

---

### Log In to the Target

{% raw %}
```shell
sudo iscsiadm -m node \
  --targetname iqn.2000-01.com.synology:synology-0.Target-1.76fd697e949 \
  --portal 192.168.2.240 \
  --login
```
{% endraw %}

---

### Verify the Active Session

{% raw %}
```shell
sudo iscsiadm --mode session --print=1
```
{% endraw %}

If successful, the disk is now visible to PBS.

---

## 🧱 Prepare the iSCSI Disk

### Format the Disk

Identify the iSCSI disk by listing all iSCSI sessions.

{% raw %}
```shell
iscsiadm -m session -P 3
```
{% endraw %}

This should display something like the following:

{% raw %}
```shell
                ************************
                Attached SCSI devices:
                ************************
                Host Number: 2  State: running
                scsi2 Channel 00 Id 0 Lun: 1
                        Attached scsi disk sdb          State: running

```
{% endraw %}

The above example shows that the iSCSI device is attached `/dev/sdb`.

Format the disk using `ext4`. Skip this step if the disk has been previously formatted and you just want to reuse the disk.

{% raw %}
```shell
sudo mkfs.ext4 /dev/sdb
```
{% endraw %}

---

### Mount the Disk

Create the mount point:

{% raw %}
```shell
sudo mkdir -p /mnt/datastore/backups
```
{% endraw %}

Mount the disk:

{% raw %}
```shell
sudo mount /dev/sda /mnt/datastore/backups
```
{% endraw %}

---

## 🔁 Persist iSCSI Across Reboots

### Enable Automatic iSCSI Login

Discover targets again to identify paths:

{% raw %}
```shell
sudo iscsiadm -m discovery -t st -p 192.168.20.240
```
{% endraw %}
This outputs something like the following,

{% raw %}
```shell
192.168.20.240:3260,1 iqn.2000-01.com.synology:synology-0.Target-1.76fd697e949
[fe80::211:32ff:fe8a:51d9]:3260,1 iqn.2000-01.com.synology:synology-0.Target-1.76fd697e949
192.168.20.2:3260,1 iqn.2000-01.com.synology:synology-0.Target-1.76fd697e949
[fe80::211:32ff:fe8a:51da]:3260,1 iqn.2000-01.com.synology:synology-0.Target-1.76fd697e949
```
{% endraw %}
Edit each `default` file under:

{% raw %}
```
/etc/iscsi/nodes/<IQN>/<IP,PORT>/default
```
{% endraw %}

Using the discovery example values,

{% raw %}
```shell
/etc/iscsi/nodes/iqn.2000-01.com.synology\:synology-0.Target-1.76fd697e949/192.168.20.240\,3260\,1/default
```
{% endraw %}

Set:

{% raw %}
```ini
node.startup = automatic
```
{% endraw %}

---

### Automatically Mount the Disk

Label the disk:

{% raw %}
```shell
sudo e2label /dev/sdb backups
```
{% endraw %}

Add to `/etc/fstab`:

{% raw %}
```shell
LABEL=backups  /mnt/datastore/backups  ext4  _netdev  0  0
```
{% endraw %}

---

## 🗂️ Add the iSCSI Storage as a PBS Datastore

1. Open the PBS Web UI
2. Go to **Datastore → Add Datastore**
3. Name: `backups`
4. Backing Path: `/mnt/datastore/backups`
5. Click **Add**

---

## 🔌 Integrate PBS with Proxmox VE

To enable backups directly from PVE:

1. Open the PVE Web UI (e.g. `https://pve-0.refol.us:8006`)
2. Navigate to **Datacenter → Storage**
3. Click **Add → Proxmox Backup Server**
4. Provide:

   * ID
   * Server
   * Username
   * Password
   * Datastore

---

## 📚 References

* Proxmox Backup Server – Getting Started
  [https://www.proxmox.com/en/proxmox-backup-server/get-started](https://www.proxmox.com/en/proxmox-backup-server/get-started)
* Debian Open-iSCSI Documentation
  [https://wiki.debian.org/SAN/iSCSI/open-iscsi](https://wiki.debian.org/SAN/iSCSI/open-iscsi)