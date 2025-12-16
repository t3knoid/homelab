---
title: "Proxmox Backup Server"
---

# Proxmox Backup Server

The Proxmox Backup Server (i.e. PBS) is installed on the third Proxmox Virtual Environment node, [pve-2](https://pve-2.refol.us:8007/). A local datastore is also available and is used to sync backups from the iscsi target for redundancy. A second installation of PBS is installed on [pve-1](https://pve-1.refol.us:8007/). It is used to sync backups from pve-2 to its local datastore for more redundancy. It uses an iSCSI target located on a [Synology](../synology/README.md) NAS device for its datastore.

## Proxmox Backup Server Installation

The [Proxmox Backup Server installation](https://pbs.proxmox.com/docs/installation.html#install-proxmox-backup-server-on-debian) uses Debian's APT package management tool. This requires configuring the apt source.list file in order to access the PBS package.

Edit the /etc/apt/sources.list file and add the following.

``` shell
# Proxmox Backup Server pbs-no-subscription repository provided by proxmox.com,
# NOT recommended for production use
deb http://download.proxmox.com/debian/pbs bookworm pbs-no-subscription
```

Download the GPG signature that's required by APT to trust the Proxmox Backup Server repository.

``` shell
sudo wget https://enterprise.proxmox.com/debian/proxmox-release-bookworm.gpg -O /etc/apt/trusted.gpg.d/proxmox-release-bookworm.gpg
```

Finally, install PBS with the following commands:

``` shell
sudo apt update
sudo apt install proxmox-backup
```

## Proxmox Backup Client Installation

Optionally install the [PBS client software](https://pbs.proxmox.com/docs/installation.html#proxmox-backup-client-only-repository). Create a new file, /etc/apt/sources.list.d/pbs-client.list, with the following content.

``` shell
deb http://download.proxmox.com/debian/pbs-client bookworm main
```

Install the backup client with the following commands.

``` shell
sudo apt update
sudo apt install proxmox-backup-client
```

## Access to the Proxmox Backup Server

After successfully installing the Proxmox Backup Server, it should be accessible on port 8007 of the host IP address or hostname.

[https://pve-2.refol.us:8007](https://pve-2.refol.us:8007)

Login using the default root@pam user.

## Configuring the iSCSI Datastore

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

``` shell
sudo apt update
sudo apt install open-scsi
sudo systemctl enable open-iscsi
sudo systemctl enable iscsid
```

#### Discover the Target

Verify the iSCSI target with the following command where the iSCSI target host (i.e. Synology server) has an IP address of 192.168.2.240.

``` shell
sudo iscsiadm -m discovery -t st -p 192.168.2.240
```

This should return the target properties similar to the following.

>192.168.2.240:3260,1 iqn.2000-01.com.synology:synology-0.Target-1.76fd697e949
[fe80::211:32ff:fe8a:51d9]:3260,1 iqn.2000-01.com.synology:synology-0.Target-1.76fd697e949
192.168.2.240:3260,1 iqn.2000-01.com.

#### Login to the target

Using the IQN number and target host IP address, use the following command to open a session with target.

``` shell
sudo iscsiadm -m node --targetname iqn.2000-01.com.synology:synology-0.Target-1.76fd697e949 --portal 192.168.2.240 --login
```

#### Verify the iSCSI Session

The device should now be available locally in the Proxmox Backup Server. Verify using the following command.

``` shell
sudo iscsiadm --mode session --print=1
```

### Prepare the iSCSI Disk for Use

Before the iSCSI disk can be used, it must be formatted and mounted to the Proxmox Backup Server's file system.

#### Format the iSCSI Disk

A new /dev/sd*x* device should now be available (e.g. /dev/sda). This device is linked to /dev/disk/by-ath/ip-* device. Format the disk as an ext4 file system.

``` shell
sudo mkfs.ext4 /dev/sda
```

#### Mount iSCSI Target

The formatted disk can now be mounted just like any local drive.

Create the mount point, in this case */mnt/datastore/backups*. 

``` shell
sudo mkdir -p /mnt/datastore/backups
```

Mount the iSCSI drive to the mount point assuming the drive is /dev/sda.

``` shell
sudo mount /dev/sda /mnt/datastore/backups
```

#### Automatically Login to iSCSI Target on Boot

The **node.start** parameter of the target must be set to automatic. The default configuration file is located under the /etc/iscsi/nodes/**iqn**/**network**/default folder.

Use the discover command to enumerate the **iqn** and **network** values.

``` shell
sudo iscsiadm -m discovery -t st -p 192.168.2.240
```

The output should something similar to the following:

``` shell
192.168.2.240:3260,1 iqn.2000-01.com.synology:synology-0.Target-1.76fd697e949
[fe80::211:32ff:fe8a:51d9]:3260,1 iqn.2000-01.com.synology:synology-0.Target-1.76fd697e949
```

There are two discovered targets (one for IPv4 and one for IPv6). Using the values from the above output, the two default files are expected in the following:

``` shell
/etc/iscsi/nodes/iqn.2000-01.com.synology:synology-0.Target-1.76fd697e949/192.168.2.240,3260,1/default
 /etc/iscsi/nodes/iqn.2000-01.com.synology:synology-0.Target-1.76fd697e949/fe80::211:32ff:fe8a:51d9,3260,1/default
```

Edit each file and find **node.start** parameter to automatic.

``` ini
node.startup = automatic
```

#### Automatically Mount the iSCSI Target on Boot

Adding an entry in /etc/fstab will automatically mount the iSCSI drive to the Proxmox Backup Server file system. The e2label tool will be used to label the formatted iscsi device to simplify identification in fstab.

The following labels /dev/sda to *backups*.

``` shell
sudo e2label /dev/sda backups
```

In /etc/fstab, add the following entry

``` shell
LABEL=backups   /mnt/datastore/backups  ext4    _netdev 0       0
```

## Use the iSCSI Drive as a Datastore

Use the following [steps to add the mounted iSCSI drive as a datastore location](https://pbs.proxmox.com/docs/storage.html#datastore-intro).

1. Open the Proxmox Backup Server web UI (e.g. [https://192.168.2.215:8007](https://192.168.2.215:8007/)). 
2. Click on Datastore > Add Datastore.
3. Provide a name (e.g. backups).
4. Enter */mnt/datastore/backups* in the *Backing Path* field.
5. Click Add to complete.

## Integrate Proxmox Backup Server with Proxmox Virtual Environment

Use the following to [integrate the proxmox Backup Server with the Proxmox Virtual Environment](https://pbs.proxmox.com/docs/pve-integration.html).

1. Open the Proxmox Virtual Environment node web UI (e.g. http://192.168.2.200:8006)
2. Select Datacenter > Storage.
3. Click Add > Proxmox Backup Server.
4. Enter the required fields, ID, Server, Username, Password, and Datastore.

## Reference

- https://www.proxmox.com/en/proxmox-backup-server/get-started
- https://wiki.debian.org/SAN/iSCSI/open-iscsi

 