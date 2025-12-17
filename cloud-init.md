---
title: "Cloud-Init"
---

# Cloud-Init

The following provides instructions on creating a Cloud-Init ready Ubuntu 24.04 template using Proxmox. These instructions were derived from [Proxmox Cloud-Init Support documentation](https://pve.proxmox.com/wiki/Cloud-Init_Support).

These steps have been automated using the [cloudinit role](https://homelab.refol.us/projects/home-lab/repository/ansible/revisions/main/entry/roles/cloudinit/README.md).

## SSH Into A Proxmox Server

The subsequent commands will be executed inside the proxmox server that will host the template. Therefore, first connect to the server's console.

{% raw %}
``` shell
ssh 192.168.2.202
```
{% endraw %}

## Download Ubuntu 24 Cloud-Init Image

{% raw %}
``` shell
wget https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img
```
{% endraw %}

## Create a new VM with VirtIO SCSI controller

{% raw %}
``` shell
qm create 9500 --memory 2048 --net0 virtio,bridge=vmbr0 --scsihw virtio-scsi-pci
```
{% endraw %}

## Attached the Disk Image to the VM

The following command will import the downloaded image into the Proxmox cluster shared storage, linstor_storage, and attach it to the VM's SCSI drive.

{% raw %}
``` shell
qm set 9500 --scsi0 linstor_storage:0,import-from=/root/noble-server-cloudimg-amd64.img
```
{% endraw %}

## Add Cloud-Init CD-ROM drive

The next step is to configure a CD-ROM drive, which will be used to pass the Cloud-Init data to the VM.

{% raw %}
``` shell
qm set 9500 --ide2 linstor_storage:cloudinit
```
{% endraw %}

## Restrict Boot to SCSI Device

To be able to boot directly from the Cloud-Init image, set the boot parameter to order=scsi0 to restrict BIOS to boot from this disk only. This will speed up booting, because VM BIOS skips the testing for a bootable CD-ROM.

{% raw %}
``` shell
qm set 9500 --boot order=scsi0
```
{% endraw %}

## Serial Console

For many Cloud-Init images, it is required to configure a serial console and use it as a display. If the configuration doesn’t work for a given image however, switch back to the default display instead.

{% raw %}
``` shell
qm set 9500 --serial0 socket --vga serial0
```
{% endraw %}

### Convert to Template

{% raw %}
```bash
qm template 9500
```
{% endraw %}

