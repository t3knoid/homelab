# Ubuntu 24.04 Server VM Template

The following documents the process of creating an Ubuntu 24.0.4 Proxmox template.

## Pre-requisites

The following are required prior to implementing these steps.

- Proxmox Virtual Environment
- Ubuntu 24.04 live server ISO image

## Create the Virtual Machine

Upload the Ubuntu 24.04 iso image into the Proxmox VE before continuining. The image is available for [download from Ubuntu](https://ubuntu.com/download/server).

### Create VM

Click on the **Create VM** button from the Proxmox top menu ribbon. 

On the *General* screen,

1. Enter *ubuntu-server-24.04* in the **Name** field.
2. Click **Next** to continue.

On the **OS** screen,

1. Select the **Use CD/DVD disc image file (iso)** combo-box selection.
2. Choose the storage location containing the Ubuntu ISO image from the **Storage** field.
3. Select the Ubuntu 24.04 ISO image (e.g., ubuntu-24.04.1-live-server-amd64.iso) fromt he ISO image field.
4. For the **Guest OS** options, select *Linux* for the **Type** and *6.x-2.6 Kernel* for the **Version**.
5. Click **Next** to continue.

On the **System** screen,

1. Select *Default* for the **Graphic card**.
2. Select *q35* for the **Machine**.
3. Use the *Default (SeaBIOS)* for the **BIOS**.
4. Select *VirtIO SCSI single* for the SCSI Controller.
5. Tick the **Qemu Agent** checkbox.
6. Click **Next** to continue.

On the **Disks** screen,

1. Select VirtIO Block for the **Bus/Device** selection.
2. Select a storage location for the **Storage** selection.
3. Configure a desired disk size in the **Disk size (GiB) selection**.
4. Click **Next** to continue.

On the CPU screen,

1. Select *1* in the **Sockets** field.
2. Select *4* in the **Cores** field.
3. Select *host* in the **Type** field.
4. Click **Next** to continue.

On the **Memory** screen,

1. Select *2048* in the **Memory (MiB)** field.
2. Select *2048* in the **Minimum memory (MiB)** field
2. Tick the **Ballooning Device** checkbox.
3. Click **Next** to continue.

On the **Network** screen, 

1. Select *VirtIO (paravirtualized)* in he **Model** field.
2. Click **Next** to continue.

On the **Confirm** screen,

1. Verify the selected settings shown are correct.
2. Tick the **Start after created** checkbox.
3. Click **Finish** to continue and create the VM. The VM will be started after creation.

## Ubuntu 24.04 Installation

1. Select the new VM and click on **>_ Console**.
2. From the Console, select **Try or Install Ubuntu** and press enter.
3. Select *English* from the **Welcome** screen and press **Enter**.
4. Press **Done** to keep the default Keyboard layout and variant settings.
5. Select *Ubuntu Server (minimized)* base installation type and press **Done*
6. Press **Done** on the **Network configuration** screen.
7. Press **Done** on the **Proxy Configuration** screen.
8. Press **Done** on the **Ubuntu archive mirror configuration** screen.
9. Press **Done** on the **Guided storage configuration** screen.
10. Press **Done** on the **Storage configuration** screen.
11. Select and press **Continue** to **Confirm destructive action**.
12. Enter appropriate entries (e.g. username, password) in the **Profile configuration** screen. Press **Done** to continue.
13. Press **Continue** on the **Upgrade to Ubuntu Pro** screen. 
14. Select **Install OpenSSH server** on the SSH configuration screen. Press **Done** to continue.
15. Select the following server snaps to install, microk8s, docker, powershell, aws-cli. Press **Done** to continue.

The Ubuntu 24.04 installation should start at this point.

Reboot the VM after installation.

## Post Installation

Perform the following after the Ubuntu installation.

### Unmount Ubuntu 24.04 ISO

Select the VM from the Proxmox VE UI. Click on **Hardware**. Select **CD/DCD Drive** and click **Edit**. Select **Do not use any media** from the combo-box selection and click **OK**.

### Install qemu-guest-agent

```bash
sudo apt update
sudo apt upgrade
sudo apt install qemu-guest-agent
sudo systemctl start qemu-guest-agent
sudo systemctl enable qemu-guest-agent
```

### Install net-tools package

```bash
sudo apt install net-tools
```

### Install VIM package

```bash
sudo apt install vim
```

### Required Packages to Join Active Directory Domain

```bash
sudo apt -y install realmd sssd sssd-tools libnss-sss libpam-sss adcli samba-common-bin oddjob oddjob-mkhomedir packagekit
```

## Convert to Template

To convert the VM into a template, do the following from the Proxmox Web GUI,

1. Select the VM.
2. Click on More > Convert to Template.
3. Click **Yes** to confirm converting to template.

## Cloning the Template

To clone the template into a new VM, do the following from the Proxmox Web GUI,

1. Select the VM.
2. Right-click and select **Clone**.
3. Select a **Target node** to create the new VM ito.
4. Select *Full CLone* from the Mode selection.
5. Enter an appropriate name in the **Name** field.
6. Press **Clone**.

### Set Static IP Address on VM

After the VM has been cloned, boot the VM. Edit the /etc/netplan/50-cloud-init.yaml file and modify the network setting using the following as a template.

```bash
network:
    ethernets:
        enp6s18:
          addresses:
            - 192.168.2.101/24
          nameservers:
            addresses:
            - 192.168.2.252
            - 192.168.2.253
            - 192.168.2.254
            search:
            - refol.us
          routes:
            - to: default
              via: 192.168.2.1
    version: 2
```

Execute the following command after saving the file.

```bash
sudo netplan apply
```

Modify the IP address shown under the **addresses** key to the desired static IP address.

### Modify hostname

Use hostnamectl to change the hostname as shown here. Change the *desired-hostname* to the new hostname.

```bash
sudo hostnamectl hostname desired-hostname
```

## References

- [Server-World.info Ubuntu 24.04 Configuration](https://www.server-world.info/en/note?os=Ubuntu_24.04&p=sysstat&f=1)