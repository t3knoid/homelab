---
title: "Installing Home Assistant on Proxmox Using a Bash Script"
---

# Installing Home Assistant on Proxmox Using a Bash Script

This guide describes how to **manually install Home Assistant OS on Proxmox VE** by importing the official QCOW2 disk image and attaching it to a virtual machine. It also provides a **single Bash script** that consolidates all manual steps into a repeatable workflow.

The instructions are based on the official [Home Assistant Linux installation documentation](https://www.home-assistant.io/installation/linux/) and adapted specifically for Proxmox VE.

The target audience is expected to be comfortable with:

- Proxmox CLI (`qm`, `pvesh`)
- Basic Bash scripting
- Virtual machine concepts (UEFI, VirtIO, SCSI)

---

## Prerequisites

Before proceeding, ensure the following requirements are met:

- **Proxmox VE 7+** installed and accessible
- **Root access** to the Proxmox node
- **QEMU Guest Agent support** installed and enabled in Proxmox (`--agent enabled=1`)
- **Sufficient resources** for the VM: minimum 2 GB RAM and 2 CPU cores
- **Networking** configured on Proxmox with a bridge (e.g., `vmbr0`) connected to your LAN
- **Required tools** installed on the Proxmox host: `curl`, `unxz`, `awk`, `grep`, and `sed`
- **Internet access** from the Proxmox host to download the Home Assistant OS image

> [!TIP] Enable QEMU Guest Agent
> Enabling the QEMU guest agent is essential for detecting the VM's IP address automatically.

---

## Manual Step-by-Step Instructions

### 1. Create the Virtual Machine (without disks)

Create a new virtual machine with the following configuration:

- **Machine**: Q35
- **BIOS**: OVMF (UEFI)
- **Memory**: 2 GB RAM (minimum recommended)
- **CPU**: 2 vCPU (e.g., 1 socket × 2 cores), `type=host`
- **SCSI Controller**: VirtIO SCSI single
- **Network**: 1 VirtIO NIC bridged to `vmbr0`

> [!IMPORTANT]
> Do **not** create or attach any disks at this stage.
> Do **not** start the VM after creation.

You can create the VM from the Proxmox Web UI or from a Proxmox node shell as `root`:

{% raw %}
```bash
# Allocate the next available VMID
VMID=$(pvesh get /cluster/nextid)

# Create a minimal VM
qm create "$VMID" --name home-assistant --memory 2048 --net0 virtio,bridge=vmbr0

# Apply detailed hardware settings
qm set "$VMID" \
  --cores 2 \
  --sockets 1 \
  --cpu host \
  --machine q35 \
  --bios ovmf \
  --ostype l26 \
  --scsihw virtio-scsi-single \
  --agent enabled=1
```
{% endraw %}

> [!NOTE]
> The VMID is dynamically assigned by querying the next available ID from the Proxmox cluster.

---

### 2. Create and Attach an EFI Disk

Because the VM uses **OVMF (UEFI)**, an EFI system disk must be created and attached:

{% raw %}
```bash
qm set "$VMID" --efidisk0 "local:1,format=raw"
```
{% endraw %}

This disk stores UEFI variables and is required for proper booting.

---

### 3. Download the Home Assistant OS Disk Image

Download the official Home Assistant OS QCOW2 image from GitHub:

{% raw %}
```bash
curl -L -o /tmp/haos_ova-16.3.qcow2.xz \
  https://github.com/home-assistant/operating-system/releases/download/16.3/haos_ova-16.3.qcow2.xz
```
{% endraw %}

---

### 4. Extract the QCOW2 Image

Extract the disk image in place:

{% raw %}
```bash
unxz /tmp/haos_ova-16.3.qcow2.xz
```
{% endraw %}

> [!TIP]
> The extracted disk image will be located at `/tmp/haos_ova-16.3.qcow2`.

---

### 5. Import the Disk into Proxmox Storage

{% raw %}
```bash
qm importdisk "$VMID" /tmp/haos_ova-16.3.qcow2 local --format qcow2
```
{% endraw %}

> [!TIP] Disk Volume ID
> This command typically reports the disk volume ID as `local:VMID/vm-VMID-disk-0.qcow2`.
> You will need this identifier in the next step.

---

### 6. Attach the Imported Disk

{% raw %}
```bash
qm set "$VMID" --scsi0 local:$VMID/vm-$VMID-disk-0.qcow2
```
{% endraw %}

---

### 7. Configure the Boot Order

{% raw %}
```bash
qm set "$VMID" --boot order=scsi0
```
{% endraw %}

---

### 8. Start the Virtual Machine

{% raw %}
```bash
qm start "$VMID"
```
{% endraw %}

Home Assistant OS will automatically resize the disk and complete initialization. After a few minutes, it should be reachable via:

{% raw %}
```
http://homeassistant.local:8123
```
{% endraw %}

---

### Tip: Finding the VM’s IP Address

To obtain the **actual VM IP address** assigned by your network’s DHCP server:

**From the Proxmox host:**

{% raw %}
```bash
qm guest cmd <VMID> network-get-interfaces
```
{% endraw %}

- Requires the **QEMU guest agent** (already enabled in this setup).
- Look for the interface named `enp6s18` and note the associated IPv4 address.

**From the Proxmox Web UI:**

- Select the VM → **Summary** → Check **IPs** once the guest agent reports it.

**Fallback (DHCP lease lookup):**

- Check your router or DHCP server for a lease named `homeassistant`.
- Alternatively, match the VM’s MAC address (visible in Proxmox) to the DHCP lease.

> [!TIP]
> Avoid using IP addresses inside Home Assistant containers (e.g., `172.x.x.x`), as those are internal Docker addresses.

---

## Full Bash Script

{% raw %}
```bash
#!/bin/bash
# Prerequisites: Proxmox VE 7+, QEMU guest agent, root access, curl, unxz, awk

set -euo pipefail

VMID=$(pvesh get /cluster/nextid)
IMAGE=haos_ova-16.3.qcow2
VERSION=16.3
STORAGE=local
FORMAT=qcow2

# Create VM
qm create "$VMID" --name home-assistant --memory 2048 --net0 virtio,bridge=vmbr0

qm set "$VMID" \
  --cores 2 \
  --sockets 1 \
  --cpu host \
  --machine q35 \
  --bios ovmf \
  --ostype l26 \
  --scsihw virtio-scsi-single \
  --agent enabled=1 \
  --serial0 socket \
  --vga serial0

# Create EFI disk
qm set "$VMID" --efidisk0 "$STORAGE:1,format=raw"

# Download and extract Home Assistant OS
if [ ! -f /tmp/$IMAGE ]; then
  curl -L -o "/tmp/$IMAGE.xz" \
    "https://github.com/home-assistant/operating-system/releases/download/$VERSION/$IMAGE.xz"
  unxz "/tmp/$IMAGE.xz"
fi

# Import disk and capture resulting disk identifier
DISK=$(qm importdisk "$VMID" "/tmp/$IMAGE" "$STORAGE" --format "$FORMAT" \
  | awk -F"'" '/^unused[0-9]+:/ {print $2; exit}')

# Attach disk and configure boot
qm set "$VMID" --scsi0 "$DISK"
qm set "$VMID" --boot order=scsi0

# Start VM
echo "Starting VM $VMID"
qm start "$VMID"
echo "VM $VMID started"

# Wait for VM to report an IP
echo "Waiting for VM IP..." 
until qm guest cmd "$VMID" network-get-interfaces 2>/dev/null | grep -q '"ip-address"'; do sleep 2; done

# Get IP address
IP_ADDRESS=$(qm guest exec "$VMID" ip route 2>/dev/null | grep -oP '"out-data"\s*:\s*"\K([^"]+)' | awk -F'\' '{print $1}' | cut -d" " -f9)

echo "VMID: $VMID"
echo "IP ADDRESS: $IP_ADDRESS"

# Wait for Home Assistant web interface
echo "Waiting for web interface..."
while ! curl -s http://$IP_ADDRESS:8123 >/dev/null; do sleep 5; done
echo "Home Assistant is ready at http://$IP_ADDRESS:8123"

# Cleanup
rm -f "/tmp/$IMAGE"
```
{% endraw %}

---

## Related Links

* [Home Assistant Linux installation](https://www.home-assistant.io/installation/linux/)
* [Home Assistant OS releases](https://github.com/home-assistant/operating-system)
* [Full Script available in GitHub gist](https://gist.github.com/t3knoid/4555225d14d05a45188a348859193451)