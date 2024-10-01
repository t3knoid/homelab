# Proxmox Virtual Machine Agent Install

In order to get information from Virtual Machines, a [guest agent](https://pve.proxmox.com/wiki/Qemu-guest-agent) is installed in the virtual machine.

## Linux

Perform the following to install the guest agent in a Linux operating system.

```bash
apt-get install qemu-guest-agent
systemctl start qemu-guest-agent
systemctl enable qemu-guest-agent
```

## Windows

Download and mount the [Windows VirtIO Drivers ISO file](https://pve.proxmox.com/wiki/Windows_VirtIO_Drivers). Execute the agent installer inside the guest-agent folder.
