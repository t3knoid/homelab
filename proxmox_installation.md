---
title: "Proxmox installation"
---

# Proxmox installation

The [installation of Proxmox VE](https://www.proxmox.com/en/proxmox-virtual-environment/get-started) is pretty straightforward. It's a matter of downloading the ISO image and copy it to a USB drive using [Balena Etcher](https://etcher.balena.io/), booting the USB drive and starting the installation.

## Configure No Subscription APT Source

After the installation, the Proxmox No subscription APT sources must be added to the Apt source list file and comment out the Proxmox Enterprise APT source list.

Edit /etc/apt/sources.list.

{% raw %}
```bash
vi /etc/apt/sources.list
```
{% endraw %}
Add the Proxmox VE no subscription repository.

{% raw %}
```bash
deb http://download.proxmox.com/debian/pve bookworm pve-no-subscription
```
{% endraw %}

Edit the Proxmox Enterprise APT source list.

{% raw %}
``` shell
vi /etc/apt/sources.list.d/pve-enterprise.list
```
{% endraw %}

Comment out the following line.

{% raw %}
``` shell
# deb https://enterprise.proxmox.com/debian/pve bookworm pve-enterprise
```
{% endraw %}

Execute ```apt update``` afterwards.

## Joining Proxmox Hosts to Active Directory

[Join Proxmox host to active directory](join_proxmox_host_to_active_directory.md) details the process on joining each Proxmox node to active directory.


## Proxmox Virtual Machine Agent Install

In order to get information from Virtual Machines, a [guest agent](https://pve.proxmox.com/wiki/Qemu-guest-agent) is installed in the virtual machine.

### Linux

Perform the following to install the guest agent in a Linux operating system.

{% raw %}
```bash
apt-get install qemu-guest-agent
systemctl start qemu-guest-agent
systemctl enable qemu-guest-agent
```
{% endraw %}

### Windows

Download and mount the [Windows VirtIO Drivers ISO file](https://pve.proxmox.com/wiki/Windows_VirtIO_Drivers). Execute the agent installer inside the guest-agent folder.

