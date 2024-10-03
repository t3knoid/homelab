# Proxmox Backup Server


## Installation

The Proxmox server is installed as a [Proxmox virtual machine](https://pve.proxmox.com/pve-docs/chapter-qm.html). It uses an iSCSI storage located on a [Synology](../synology/README.md) NAS device.

### Prepare Proxmox Backup Server Installation ISO Image
1. Download the Proxmox Backup Server installation ISO image from https://www.proxmox.com/en/downloads/proxmox-backup-server.
2. Upload the ISO image into the Proxmox server local storage.
3. Click on Create VM to start the VM creation process.

### Virtual Machine Hardware Properties

The following hardware properties are used when creating the virtual machine:

- Memory: 2.00 GiB
- Processors: 4 (1 societs, 4 cores)[host]
- BIOS: Default (SeaBIOS)
- Display Default
- Machine: Default (i440fx)
- SCSI Controller: VirtIO SCSI single
- CD/DVD Drive (ide2)
- Hard Disk (scsi0): 32G
- Hard Disk (scsi1): iscsi
- Network Device (net0): bridge=vmbr0


## iSCSI Device

### Synology

### Proxmox Backup Server


## Prepare Datastore

The mounted iSCSI device hosted in a Synology server will be used as a datastore. 

##

Select Administration > Storage/Disks. Select the device (e.g., /dev/sdb) and choose **Initialize Disk with GPT**.

Select the Directory tab. Click on the **Create: Directory** button.

Click on 

## Configure No Subscription APT Source

After the installation, the Proxmox No subscription APT source must be added to the Apt source list file and comment out the Proxmox Enterprise APT source list.

Edit /etc/apt/sources.list.

```bash
vi /etc/apt/sources.list
```
Add the Proxmox VE no subscription repository.

```bash
deb http://download.proxmox.com/debian/pve bookworm pve-no-subscription
```

Edit the Proxmox Backup Server Enterprise APT source list.

```bash
vi /etc/apt/sources.list.d/pbs-enterprise.list
```

Comment out the following line.

```bash
#deb https://enterprise.proxmox.com/debian/pbs bookworm pbs-enterprise
```

Execute ```apt update``` afterwards.

## Joining Proxmox Backup Server Host to Active Directory

Joining a Proxmox Backup Server host to active directory is detailed in the [Join a Proxmox Host to Active Directory Domain](join_a_proxmox_host_to_active_directory_domain.md) document.

## Reference

- https://www.proxmox.com/en/proxmox-backup-server/get-started
