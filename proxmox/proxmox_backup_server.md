# Proxmox Backup Server
- [Summary](#summary)
- [Zotac Zbox P1331](#zotac-zbox-p1331)
  - [Zbox Hardware Specification](#zbox-hardware-specification)
- [Debian 12 Installation](#debian-12-installation)
- [Join Proxmox Backup Server Host to Active Directory](#join-proxmox-backup-server-host-to-active-directory)
- [Proxmox Backup Server Installation](#proxmox-backup-server-installation)
- [Proxmox Backup Client Installation](#proxmox-backup-client-installation)
- [Access to the Proxmox Backup Server](#access-to-the-proxmox-backup-server)
- [Configuring the Datastore](#configuring-the-datastore)
  - [Configure the iSCSI Target](#configure-the-iscsi-target)
  - [Configure the iSCSI Initiator](#configure-the-iscsi-initiator)
    - [Install Open-SCSI Package](#install-open-scsi-package)
    - [Discover the Target](#discover-the-target)
    - [Login to the target](#login-to-the-target)
    - [Verify the iSCSI Session](#verify-the-iscsi-session)
  - [Prepare the iSCSI Disk for Use](#prepare-the-iscsi-disk-for-use)
    - [Format the iSCSI Disk](#format-the-iscsi-disk)
    - [Mount iSCSI Target](#mount-iscsi-target)
    - [Automatically Login to iSCSI Target on Boot](#automatically-login-to-iscsi-target-on-boot)
    - [Automatically Mount the iSCSI Target on Boot](#automatically-mount-the-iscsi-target-on-boot)
- [Use the iSCSI Drive as a Datastore](#use-the-iscsi-drive-as-a-datastore)
- [Integrate Proxmox Backup Server with Proxmox Virtual Environment](#integrate-proxmox-backup-server-with-proxmox-virtual-environment)
- [Reference](#reference)


## Summary

The Proxmox Backup Server (i.e. PBS) is installed on an old [Zotac Zbox P1331](https://www.zotac.com/download/mediadrivers/mb/man/pb309pi331.pdf). It uses an iSCSI target located on a [Synology](../synology/README.md) NAS device for its datastore.

## Zotac Zbox P1331

The Zbox came with Windows 10 installed. The plan is to install PBS using its ISO image burned into a USB dongle. Unfortunately, this wasn't possible due to a hardware incompatibility with the Zbox that causes the installer to simply freeze during installation. The alternate plan is to install [Debian 12](https://www.debian.org/releases/stable/amd64/) first then install PBS afterwards. This method worked, albeit, Debian 12 must be installed in non-graphical mode.

### Zbox Hardware Specification

The following is an abridge specification of the Zotac Zbox P1331.

- Memory: 4GB LPDDR3
- Processors: Intel Atom X5-Z8500 (quad-core, 1.44GHz up to 2.24GHz)
- Storage: 64GB eMMC
- Network Device: 1Gbps Ethernet

## Debian 12 Installation

Debian 12 was chosen because the PBS installation ISO uses the same operating system. This avoids any incompatibilities and makes the process of installing PBS simple.

The Debian 12 installation is fairly straightforward. Download the Debian 12 from https://www.debian.org/download. Use [balena Etcher](https://etcher.balena.io/) to write the ISO image into a USB drive. 

Because of the incompatibility with the video hardware in the Zbox, use the text-based installation. Furthermore, do not install a Debian desktop environment when prompted. To simplify the installation, a single partition was created using all available space in Zbox's 64GB eMMC storage.

A fixed network IP address is used by configuring /etc/network/interfaces with the following.

```bash
iface enp2s0 inet static
        address 192.168.2.215/24
        gateway 192.168.2.1
```
## Join Proxmox Backup Server Host to Active Directory

Joining a Proxmox Backup Server host to active directory is detailed in the [Join a Proxmox Host to Active Directory Domain](join_a_proxmox_host_to_active_directory_domain.md) document.

## Proxmox Backup Server Installation

The [Proxmox Backup Server installation](https://pbs.proxmox.com/docs/installation.html#install-proxmox-backup-server-on-debian) uses Debian's APT package management tool. This requires configuring the apt source.list file in order to access the PBS package.

Edit the /etc/apt/sources.ist file and add the following.

```bash
# Proxmox Backup Server pbs-no-subscription repository provided by proxmox.com,
# NOT recommended for production use
deb http://download.proxmox.com/debian/pbs bookworm pbs-no-subscription
```

Download the GPG signature that's required by APT to trust the Proxmox Backup Server repository.

```bash
sudo wget https://enterprise.proxmox.com/debian/proxmox-release-bookworm.gpg -O /etc/apt/trusted.gpg.d/proxmox-release-bookworm.gpg
```

Finally, install PBS with the following commands:

```bash
sudo apt update
sudo apt install proxmox-backup
```

## Proxmox Backup Client Installation

Optionally install the [PBS client software](https://pbs.proxmox.com/docs/installation.html#proxmox-backup-client-only-repository). Create a new file, /etc/apt/sources.list.d/pbs-client.list, with the following content.

```bash
deb http://download.proxmox.com/debian/pbs-client bookworm main
```

Install the backup client with the following commands.

```bash
sudo apt update
sudo apt install proxmox-backup-client
```

## Access to the Proxmox Backup Server

After successfully installing the Proxmox Backup Server, it should be accessible on port 8007 of the host IP address or hostname.

[https://pbs-0.refol.us:8007](https://pbs-0.refol.us:8007)

## Configuring the Datastore

Before backups can be created, a [datastore](https://pbs.proxmox.com/docs/storage.html#datastore) must be configured. An iSCSI target hosted in [Synology](../synology/README.md) NAS device will be mounted locally and used as the datastore for the backups. Synology will provide storage redundancy. 

iSCSI allows the use of network storage as if it is local to the host it is interfaced with. The two parts to iSCSI are the initiator and the target. Think of the initiator as the client to the target who is serving up the network storage.

### Configure the iSCSI Target

The iSCSI target is hosted in the Synology server. Use the following steps.
1. Login to DSM.
2. Navigate to Main menu > SAN Manager.
3. Click on iSCSI > Create
4. Click the Create button.
5. Enter a Name such as *Proxmox* and click Next.
7. Select Create a new LUN and click Next.
8. Enter a value in the *Total capacity (GB)* field. 1TB (e.g., 1024) is a good start. Set the Space allocation to *Thick Provisioning* and click Next.
9. Click Apply to confirm settings.

After the target has been created, copy the IQN value. This is needed to configure the initiator.

### Configure the iSCSI Initiator

The [iSCSI initiator](https://wiki.debian.org/SAN/iSCSI/open-iscsi) or client is the Proxmox Backup Server. the following steps are executed from the PBS console.

#### Install Open-SCSI Package

The **Open-SCSI** package must be installed first 

```bash
sudo apt update
sudo apt install open-scsi
sudo systemctl enable open-iscsi
sudo systemctl enable iscsid
```

#### Discover the Target

Verify the iSCSI target with the following command where the iSCSI target host (i.e. Synology server) has an IP address of 192.168.2.240.

```bash
sudo iscsiadm -m discovery -t st -p 192.168.2.240
```

This should return the target properties similar to the following.

>192.168.2.240:3260,1 iqn.2000-01.com.synology:synology-0.Target-1.76fd697e949
[fe80::211:32ff:fe8a:51d9]:3260,1 iqn.2000-01.com.synology:synology-0.Target-1.76fd697e949
192.168.2.240:3260,1 iqn.2000-01.com.

#### Login to the target

Using the IQN number and target host IP address, use the following command to open a session with target.

```bash
sudo iscsiadm -m node --targetname iqn.2000-01.com.synology:synology-0.Target-1.76fd697e949 --portal 192.168.2.240 --login
```

#### Verify the iSCSI Session

The device should now be available locally in the Proxmox Backup Server. Verify using the following command.

```bash
sudo iscsiadm --mode session --print=1
```

### Prepare the iSCSI Disk for Use

Before the iSCSI disk can be used, it must be formatted and mounted to the Proxmox Backup Server's file system.

#### Format the iSCSI Disk

A new /dev/sd*x* device should now be available (e.g. /dev/sda). This device is linked to /dev/disk/by-ath/ip-* device. Format the disk as an ext4 file system.

```bash
sudo mkfs.ext4 /dev/sda
```

#### Mount iSCSI Target

The formatted disk can now be mounted just like any local drive.

Create the mount point, in this case */mnt/datastore/backups*. 

```bash
sudo mkdir -p /mnt/datastore/backups
```

Mount the iSCSI drive to the mount point assuming the drive is /dev/sda.

```bash
sudo mount /dev/sda /mnt/datastore/backups
```

#### Automatically Login to iSCSI Target on Boot

The **node.start** parameter of the target must be set to automatic. The default configuration file is located under the /etc/iscsi/nodes/**iqn**/**network**/default folder.

Use the discover command to enumerate the **iqn** and **network** values.

```bash
sudo iscsiadm -m discovery -t st -p 192.168.2.240
```

The output should something similar to the following:

```bash
192.168.2.240:3260,1 iqn.2000-01.com.synology:synology-0.Target-1.76fd697e949
[fe80::211:32ff:fe8a:51d9]:3260,1 iqn.2000-01.com.synology:synology-0.Target-1.76fd697e949
```

There are two discovered targets (one for IPv4 and one for IPv6). Using the values from the above output, the two default files are expected in the following:

```bash
/etc/iscsi/nodes/iqn.2000-01.com.synology:synology-0.Target-1.76fd697e949/192.168.2.240,3260,1/default
 /etc/iscsi/nodes/iqn.2000-01.com.synology:synology-0.Target-1.76fd697e949/fe80::211:32ff:fe8a:51d9,3260,1/default
```

Edit each file and find **node.start** parameter to automatic.

```ini
node.startup = automatic
```

#### Automatically Mount the iSCSI Target on Boot

Adding an entry in /etc/fstab will automatically mount the iSCSI drive to the Proxmox Backup Server file system. The e2label tool will be used to label the formatted iscsi device to simplify identification in fstab.

The following labels /dev/sda to *backups*.

```bash
sudo e2label /dev/sda backups
```

In /etc/fstab, add the following entry

```bash
LABEL=backups   /mnt/datastore/backups  ext4    _netdev 0       0
```

## Use the iSCSI Drive as a Datastore

Use the following [steps to add the mounted iSCSI drive as a datastore location](https://192.168.2.215:8007/docs/storage.html#datastore-intro).

1. Open the Proxmox Backup Server web UI (e.g. [https://192.168.2.215:8007](https://192.168.2.215:8007/)). 
2. Click on Datastore > Add Datastore.
3. Provide a name (e.g. backups).
4. Enter */mnt/datastore/backups* in the *Backing Path* field.
5. Click Add to complete.

## Integrate Proxmox Backup Server with Proxmox Virtual Environment

The following https://pbs.proxmox.com/docs/pve-integration.html

1. Open the Proxmox Virtual Environment node web UI (e.g. http://192.168.2.200:8006)
2. Select Datacenter > Storage.
3. Click Add > Proxmox Backup Server.
4. Enter the required fields, ID, Server, Username, Password, and Datastore.

## Reference

- https://www.proxmox.com/en/proxmox-backup-server/get-started
- https://wiki.debian.org/SAN/iSCSI/open-iscsi

  