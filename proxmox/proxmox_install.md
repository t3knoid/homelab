# Proxmox Install
- [Overview](#overview)
- [Joining Proxmox Hosts to Active Directory](#joining-proxmox-hosts-to-active-directory)
- [Backup](#backup)

## Overview

The [installation of Proxmox VE](https://www.proxmox.com/en/proxmox-virtual-environment/get-started) is pretty straightforward. It's a matter of downloading the ISO image and copy it to a USB drive using [Balena Etcher](https://etcher.balena.io/), booting the USB drive and starting the installation.

After the installation, edit /etc/apt/sources.list and add the Proxmox VE no subscription repository,

```bash
deb http://download.proxmox.com/debian/pve bookworm pve-no-subscription
```

Execute ```apt update``` afterwards.

## Joining Proxmox Hosts to Active Directory

Joining a Proxmox host to active directory is detailed in the [Join a Proxmox Host to Active Directory Domain](join_a_proxmox_host_to_active_directory_domain.md) document.

## Backup
