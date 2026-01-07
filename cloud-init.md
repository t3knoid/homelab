---
title: "️ Cloud‑Init"
---

# ☁️ **Cloud‑Init**

The following provides instructions on creating a Cloud‑Init–ready Ubuntu 24.04 template using Proxmox. These instructions were derived from the [Proxmox Cloud‑Init Support documentation](https://pve.proxmox.com/wiki/Cloud-Init_Support).

These steps have been automated using the [`cloudinit` Ansible role](https://github.com/t3knoid/ansible/tree/main/roles/cloudinit).

If you are a contributor looking to **extend the system or add support for new templates**, see the  
👉 **[Contributor Guide for Adding New Cloud-Init VM Templates]**  
for details on `global_os`, template inventory, and how the automation works behind the scenes.

---

## 🔐 **SSH Into a Proxmox Server**

All commands below are executed directly on the Proxmox host that will store the template.

{% raw %}
```shell
ssh 192.168.2.202
```
{% endraw %}

---

## 📥 **Download Ubuntu 24.04 Cloud‑Init Image**

{% raw %}
```shell
wget https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img
```
{% endraw %}

---

## 🖥️ **Create a New VM (VirtIO SCSI Controller)**

{% raw %}
```shell
qm create 9500 --memory 2048 --net0 virtio,bridge=vmbr0 --scsihw virtio-scsi-pci
```
{% endraw %}

---

## 📦 **Attach the Disk Image to the VM**

Import the downloaded image into shared storage (`linstor_storage`) and attach it as the VM’s SCSI disk.

{% raw %}
```shell
qm set 9500 --scsi0 linstor_storage:0,import-from=/root/noble-server-cloudimg-amd64.img
```
{% endraw %}

---

## 💿 **Add Cloud‑Init CD‑ROM Drive**

{% raw %}
```shell
qm set 9500 --ide2 linstor_storage:cloudinit
```
{% endraw %}

---

## ⚙️ **Restrict Boot to the SCSI Device**

{% raw %}
```shell
qm set 9500 --boot order=scsi0
```
{% endraw %}

---

## 🧩 **Enable Serial Console**

Many cloud images expect a serial console. Enable it and set it as the display:

{% raw %}
```shell
qm set 9500 --serial0 socket --vga serial0
```
{% endraw %}

If the image does not boot correctly, revert to a standard display.

---

## 📁 **Convert the VM to a Template**

{% raw %}
```bash
qm template 9500
```
{% endraw %}

