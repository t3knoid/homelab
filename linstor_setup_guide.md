---
title: "Linstor Setup Guide"
---

# Linstor Setup Guide

The following is an abridged version of Linbit's [Linstor Setup Guide](https://linbit.com/blog/linstor-setup-proxmox-ve-volumes/).

## Prepare Storage

Prepare the secondary drive in each host by creating the volume group and logical volume to be used by Linstor. 

Create the volume group named linstor_vg. 

``` shell
vgcreate linstor_vg /dev/sda
```

Create a thinpool logical volume named *data*.

``` shell
lvcreate -l 100%FREE --thinpool data linstor_vg
```

## Install Components

Add the Linbit public Repo.

``` shell
wget -O /tmp/package-signing-pubkey.asc https://packages.linbit.com/package-signing-pubkey.asc
gpg --yes -o /etc/apt/trusted.gpg.d/linbit-keyring.gpg --dearmor /tmp/package-signing-pubkey.asc
PVERS=8 && echo "deb [signed-by=/etc/apt/trusted.gpg.d/linbit-keyring.gpg] http://packages.linbit.com/public/ proxmox-$PVERS drbd-9" > /etc/apt/sources.list.d/linbit.list
apt update
```

Install low-level components on all nodes.

``` shell
apt install proxmox-default-headers drbd-dkms drbd-utils
```

Install Linstor controller and satellite services on all nodes.

``` shell
apt install linstor-controller linstor-satellite linstor-client
systemctl enable linstor-satellite --now
```

Start Linstor controller on the controller node.

Connect and start the Linstor controller service to the node that will act as the controller (e.g., pve-0) 

``` shell
systemctl enable linstor-controller --now
```

## Add Nodes 

All commands from this point on are executed from the Linstor controller node.

Add nodes into the Linstor cluster.

``` shell
linstor node create pve-0 192.168.2.200
linstor node create pve-1 192.168.2.201
linstor node create pve-2 192.168.2.202
```

## Configure Storage

Create the Linstor storage pool with the 

``` shell
linstor storage-pool create lvmthin pve-0 pve-storage linstor_vg/data
linstor storage-pool create lvmthin pve-1 pve-storage linstor_vg/data
linstor storage-pool create lvmthin pve-2 pve-storage linstor_vg/data
```

Verify the storage pool.

``` shell
linstor storage-pool list
```

## Linstor Resource Groups

Create a Linstor resource group.
``` shell
linstor resource-group create pve-rg --storage-pool=pve-storage --place-count=3
```
...and its accompanying volume group.

``` shell
linstor volume-group create pve-rg
```

## Linstor Plugin Setup

Install the Linstor Proxmox plugin.

``` shell
apt install linstor-proxmox
```
Configure the plugin by editing /etc/pve/storage.cfg. Add the following section.

``` shell
drbd: linstor_storage
    content images, rootdir
    controller 192.168.2.200
    resourcegroup pve-rg
```

This file will be replicated in the other nodes after the services below are restarted.

## Restart Services

``` shell
systemctl restart pve-cluster pvedaemon pvestatd pveproxy pve-ha-lrm
```

## References

- https://linbit.com/drbd-user-guide/linstor-guide-1_0-en/#s-proxmox-installing-from-linbit-public-repos
- https://linbit.com/blog/linstor-setup-proxmox-ve-volumes/
