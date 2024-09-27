# Linstor Install

Linstor provides support of failover of VMs. It uses DRBD to provide persistent storage between the Proxmox node clusters. The storage named linstor_storage will be created to be used by virtual machines or containers.

Use the following [guide](https://linbit.com/blog/linstor-setup-proxmox-ve-volumes/) to install and configure Linstor.

## Linstor Install Overview

The following is an abridged version of the afformentioned guide.

### Prepare Storage

Prepare the secondary drive in each host by creating the volume group and logical volume to be used by Linstor. 

Create the volume group named linstor_vg. 

```bash
vgcreate linstor_vg /dev/sda
```

Create a thinpool logical volume named *data*.

```bash
lvcreate -l 100%FREE --thinpool data linstor_vg
```

### Install Components

Add the Linbit public Repo.

```bash
wget -O /tmp/package-signing-pubkey.asc https://packages.linbit.com/package-signing-pubkey.asc
gpg --yes -o /etc/apt/trusted.gpg.d/linbit-keyring.gpg --dearmor /tmp/package-signing-pubkey.asc
PVERS=8 && echo "deb [signed-by=/etc/apt/trusted.gpg.d/linbit-keyring.gpg] http://packages.linbit.com/public/ proxmox-$PVERS drbd-9" > /etc/apt/sources.list.d/linbit.list
apt update
```

Install low-level components on all nodes.

```bash
apt install proxmox-default-headers drbd-dkms drbd-utils
```

Install Linstor controller and satellite services on all nodes.

```bash
apt install linstor-controller linstor-satellite linstor-client
systemctl enable linstor-satellite --now
```

Start Linstor controller on the controller node.

Connect and start the Linstor controller service to the node that will act as the controller (e.g., pve-0) 

```bash
systemctl enable linstor-controller --now
```

### Add Nodes 

All commands from this point on are executed from the Linstor controller node.

Add nodes into the Linstor cluster.

```bash
linstor node create pve-0 192.168.2.200
linstor node create pve-1 192.168.2.201
linstor node create pve-2 192.168.2.202
```

### Configure Storage

Create the Linstor storage pool with the 

```bash
linstor storage-pool create lvmthin pve-0 pve-storage linstor_vg/data
linstor storage-pool create lvmthin pve-1 pve-storage linstor_vg/data
linstor storage-pool create lvmthin pve-2 pve-storage linstor_vg/data
```

Verify the storage pool.

```bash
linstor storage-pool list
```

### Linstor Resource Groups

Create a Linstor resource group.
```bash
linstor resource-group create pve-rg --storage-pool=pve-storage --place-count=3
```
...and its accompanying volume group.

```bash
linstor volume-group create pve-rg
```

### Linstor Plugin Setup

Install the Linstor Proxmox plugin.

```bash
apt install linstor-proxmox
```
Configure the plugin by editing /etc/pve/storage.cfg. Add the following section.

```bash
drbd: linstor_storage
    content images, rootdir
    controller 192.168.2.200
    resourcegroup pve-rg
```

This file will be replicated in the other nodes after the services below are restarted.

### Restart Services

```bash
systemctl restart pve-cluster pvedaemon pvestatd pveproxy pve-ha-lrm
```

## Changing IP Address of Clusters


systemctl stop pve-cluster
systemctl stop corosync
systemctl stop linstor-controller.service
systemctl stop linstor-satellite.service

vi /etc/corosync/corosync.conf

Change IP Addresses of each node

vi /etc/pve/storage.cfg

Change IP to controller IP

killall pmxcfs

systemctl start corosync
systemctl start pve-cluster
systemctl start linstor-controller.service
systemctl start linstor-satellite.service

### Modify Node IP Address

```bash
linstor node interface modify --ip 192.168.2.200 pve-0 default
linstor node interface modify --ip 192.168.2.201 pve-1 default
linstor node interface modify --ip 192.168.2.202 pve-2 default
```

### Verify Node Cluster

```bash
root@pve-0:~# linstor node list
╭────────────────────────────────────────────────────────╮
┊ Node  ┊ NodeType ┊ Addresses                  ┊ State  ┊
╞════════════════════════════════════════════════════════╡
┊ pve-0 ┊ COMBINED ┊ 192.168.2.200:3366 (PLAIN) ┊ Online ┊
┊ pve-1 ┊ COMBINED ┊ 192.168.2.201:3366 (PLAIN) ┊ Online ┊
┊ pve-2 ┊ COMBINED ┊ 192.168.2.202:3366 (PLAIN) ┊ Online ┊
╰────────────────────────────────────────────────────────╯
```
