# Proxmox Install
- [Overview](#overview)
- [Configure No Subscription APT Source](#configure-no-subscription-apt-source)
- [Joining Proxmox Hosts to Active Directory](#joining-proxmox-hosts-to-active-directory)

## Overview

The [installation of Proxmox VE](https://www.proxmox.com/en/proxmox-virtual-environment/get-started) is pretty straightforward. It's a matter of downloading the ISO image and copy it to a USB drive using [Balena Etcher](https://etcher.balena.io/), booting the USB drive and starting the installation.

## Configure No Subscription APT Source

After the installation, the Proxmox No subscription APT sources must be added to the Apt source list file and comment out the Proxmox Enterprise APT source list.

Edit /etc/apt/sources.list.

```bash
vi /etc/apt/sources.list
```
Add the Proxmox VE no subscription repository.

```bash
deb http://download.proxmox.com/debian/pve bookworm pve-no-subscription
```

Edit the Proxmox Enterprise APT source list.

```bash
vi /etc/apt/sources.list.d/pve-enterprise.list
```

Comment out the following line.

```bash
# deb https://enterprise.proxmox.com/debian/pve bookworm pve-enterprise
```

Execute ```apt update``` afterwards.

## Joining Proxmox Hosts to Active Directory

Joining a Proxmox host to active directory is detailed in the [Join a Proxmox Host to Active Directory Domain](join_a_proxmox_host_to_active_directory_domain.md) document.


