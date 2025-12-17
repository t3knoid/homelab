---
title: "Linstor Setup Guide"
---

# Linstor Setup Guide

The following is an abridged version of Linbit's [Linstor Setup Guide](https://linbit.com/blog/linstor-setup-proxmox-ve-volumes/).

## Prepare Storage

Prepare the secondary drive in each host by creating the volume group and logical volume to be used by Linstor. 

Create the volume group named linstor_vg. 

{% raw %}
``` shell
vgcreate linstor_vg /dev/sda
```
{% endraw %}

Create a thinpool logical volume named *data*.

{% raw %}
``` shell
lvcreate -l 100%FREE --thinpool data linstor_vg
```
{% endraw %}

## Install Components

Add the Linbit public Repo.

{% raw %}
``` shell
wget -O /tmp/package-signing-pubkey.asc https://packages.linbit.com/package-signing-pubkey.asc
gpg --yes -o /etc/apt/trusted.gpg.d/linbit-keyring.gpg --dearmor /tmp/package-signing-pubkey.asc
PVERS=8 && echo "deb [signed-by=/etc/apt/trusted.gpg.d/linbit-keyring.gpg] http://packages.linbit.com/public/ proxmox-$PVERS drbd-9" > /etc/apt/sources.list.d/linbit.list
apt update
```
{% endraw %}

Install low-level components on all nodes.

{% raw %}
``` shell
apt install proxmox-default-headers drbd-dkms drbd-utils
```
{% endraw %}

Install Linstor controller and satellite services on all nodes.

{% raw %}
``` shell
apt install linstor-controller linstor-satellite linstor-client
systemctl enable linstor-satellite --now
```
{% endraw %}

Start Linstor controller on the controller node.

Connect and start the Linstor controller service to the node that will act as the controller (e.g., pve-0) 

{% raw %}
``` shell
systemctl enable linstor-controller --now
```
{% endraw %}

## Add Nodes 

All commands from this point on are executed from the Linstor controller node.

Add nodes into the Linstor cluster.

{% raw %}
``` shell
linstor node create pve-0 192.168.2.200
linstor node create pve-1 192.168.2.201
linstor node create pve-2 192.168.2.202
```
{% endraw %}

## Configure Storage

Create the Linstor storage pool with the 

{% raw %}
``` shell
linstor storage-pool create lvmthin pve-0 pve-storage linstor_vg/data
linstor storage-pool create lvmthin pve-1 pve-storage linstor_vg/data
linstor storage-pool create lvmthin pve-2 pve-storage linstor_vg/data
```
{% endraw %}

Verify the storage pool.

{% raw %}
``` shell
linstor storage-pool list
```
{% endraw %}

## Linstor Resource Groups

Create a Linstor resource group.
{% raw %}
``` shell
linstor resource-group create pve-rg --storage-pool=pve-storage --place-count=3
```
{% endraw %}
...and its accompanying volume group.

{% raw %}
``` shell
linstor volume-group create pve-rg
```
{% endraw %}

## Linstor Plugin Setup

Install the Linstor Proxmox plugin.

{% raw %}
``` shell
apt install linstor-proxmox
```
{% endraw %}
Configure the plugin by editing /etc/pve/storage.cfg. Add the following section.

{% raw %}
``` shell
drbd: linstor_storage
    content images, rootdir
    controller 192.168.2.200
    resourcegroup pve-rg
```
{% endraw %}

This file will be replicated in the other nodes after the services below are restarted.

## Restart Services

{% raw %}
``` shell
systemctl restart pve-cluster pvedaemon pvestatd pveproxy pve-ha-lrm
```
{% endraw %}

## References

- https://linbit.com/drbd-user-guide/linstor-guide-1_0-en/#s-proxmox-installing-from-linbit-public-repos
- https://linbit.com/blog/linstor-setup-proxmox-ve-volumes/
