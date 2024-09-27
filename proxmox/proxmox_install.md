# Proxmox Install

The [installation of Proxmox VE](https://www.proxmox.com/en/proxmox-virtual-environment/get-started) is pretty straightforward. It's a matter of downloading the ISO image and copy it to a USB drive using [Balena Etcher](https://etcher.balena.io/), booting the USB drive and starting the installation.

After the installation, edit /etc/apt/sources.list and add the Proxmox VE no subscription repository,

```bash
deb http://download.proxmox.com/debian/pve bookworm pve-no-subscription
```

Execute ```apt update``` afterwards.

## Backup
