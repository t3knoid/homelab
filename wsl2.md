---
title: "WSL2"
---

# 🐧 WSL2  

*Using Ubuntu 24.04 on Windows 10/11*

This page provides an introduction to **WSL2 (Windows Subsystem for Linux v2)** and focuses on WSL usage, management, networking, hostname configuration, SSH access, and common administrative commands. Examples use **Ubuntu 24.04**, the recommended distribution.

---

## 💡 What Is WSL2?

WSL2 is a lightweight virtualization layer built into Windows that runs a **real Linux kernel** inside a highly optimized virtual machine. It provides:

- Full Linux compatibility  
- High performance and fast startup  
- Seamless integration with the Windows filesystem  
- Native networking  
- Support for Linux tools such as Python, Git, OpenSSH, Docker, and Ansible  

WSL2 behaves like a Linux VM but with far less overhead, making it ideal for development, automation, and homelab workflows.

---

## ⚙️ Why Use WSL2?

WSL2 is useful for:

- Running Linux tools on a Windows workstation  
- Development environments (Python, Node, Go, Rust, etc.)  
- Git‑based workflows  
- Container development  
- Automation and scripting  
- Running Ansible as a **Linux control node**  
- Accessing both Windows and Linux files from the same terminal  

Because WSL2 uses a real Linux kernel, it supports nearly all Linux software without modification.

For details on how to use WSL2 as an Ansible Control node,

👉 See: **[Configure WSL2 as an Ansible Control Node Runbook](configure_wsl2_as_an_ansible_control_node_runbook.md)**.

---

## 🏗️ Installing WSL2 (Ubuntu 24.04)

Open **PowerShell as Administrator**:

{% raw %}
```
wsl --install -d Ubuntu-24.04
```
{% endraw %}

If WSL is already installed:

{% raw %}
```
wsl --install
wsl --list --online
wsl --install -d Ubuntu-24.04
```
{% endraw %}

Reboot if prompted.

---

## ▶️ Starting and Stopping WSL2

### Start WSL
{% raw %}
```
wsl
```
{% endraw %}

### Start a specific distribution
{% raw %}
```
wsl -d Ubuntu-24.04
```
{% endraw %}

### Stop all WSL instances
{% raw %}
```
wsl --shutdown
```
{% endraw %}

### Stop a specific distribution
{% raw %}
```
wsl --terminate Ubuntu-24.04
```
{% endraw %}

---

## 📦 Listing and Managing Distributions

### List installed distributions
{% raw %}
```
wsl --list --verbose
```
{% endraw %}

### List available distributions
{% raw %}
```
wsl --list --online
```
{% endraw %}

### Set default distribution
{% raw %}
```
wsl --set-default Ubuntu-24.04
```
{% endraw %}

### Unregister (delete) a distribution  
*(This permanently deletes the Linux filesystem)*

{% raw %}
```
wsl --unregister Ubuntu-24.04
```
{% endraw %}

---

## 🔄 Updating Ubuntu 24.04

Inside WSL:

{% raw %}
```
sudo apt update && sudo apt upgrade -y
```
{% endraw %}

---

## 🌐 WSL2 Networking: IP Address and Hostname

WSL2 uses a **virtualized NAT network**. This affects IP addressing, hostname resolution, and SSH access.

---

### 📡 WSL2 IP Address

Inside WSL:

{% raw %}
```
ip addr show eth0
```
{% endraw %}

Typical values:

- IP: `172.29.x.x`  
- Gateway: `172.29.x.1`

**Note:**  
WSL2 IP addresses are **dynamic** and change every time WSL restarts.

---

### 🧭 Static IP Support

**WSL2 does not support static IP assignment.**

Because WSL2 uses a lightweight NAT‑based virtual network, the IP is recreated on each boot.

---

### 🏷️ Configuring the WSL2 Hostname

Inside WSL:

- Edit /etc/wsl.conf
- Add the following,

{% raw %}
```bash
[network]
hostname = my-wsl-node
generateHosts = false
```
{% endraw %}
- Shutdown WSL completely using the following command from the Windows PowerShell,

{% raw %}
```bash
wsl --shutdown
```
{% endraw %}
- Restart WSL


---

## 🔐 Connecting to the WSL2 Host Using SSH

WSL2 can run an OpenSSH server, allowing SSH access from **Windows** or even **other machines** (with port forwarding).

---

### 🛠️ Step 1 — Install and Enable OpenSSH Server

Inside WSL:

{% raw %}
```
sudo apt install openssh-server
sudo systemctl enable ssh
sudo systemctl start ssh
```
{% endraw %}

---

### 🌍 Step 2 — Find the WSL2 IP Address

{% raw %}
```
ip -4 addr show eth0
```
{% endraw %}

Example:

{% raw %}
```
172.29.112.5
```
{% endraw %}

---

### 💻 Step 3 — SSH from Windows

From PowerShell or CMD:

{% raw %}
```
ssh <username>@<wsl-ip>
```
{% endraw %}

Example:

{% raw %}
```
ssh frank@172.29.112.5
```
{% endraw %}

---

### 🌐 SSH From Another Machine (LAN Access)

WSL2 is behind a NAT and **not directly reachable** from the LAN.

To allow external SSH access, configure Windows port forwarding:

{% raw %}
```
netsh interface portproxy add v4tov4 listenport=22 listenaddress=0.0.0.0 connectport=22 connectaddress=<WSL-IP>
```
{% endraw %}

Then allow the firewall rule:

{% raw %}
```
New-NetFirewallRule -DisplayName "WSL SSH" -Direction Inbound -Protocol TCP -LocalPort 22 -Action Allow
```
{% endraw %}

You can then SSH from another machine using the **Windows host’s LAN IP**.

> ℹ️ **NOTE**
> The IP address of the WSL host changes whenever it restarts, which requires configuring Windows port forwarding.

---

## 📁 Accessing Windows Files from WSL

Windows drives are mounted under `/mnt`:

{% raw %}
```
/mnt/c/Users/<username>/Documents
/mnt/d/
```
{% endraw %}

You can:

- Work directly in Windows folders  
- Clone repositories into WSL for better performance  
- Use symbolic links between environments  

---

## 🧰 Useful WSL Commands (Quick Reference)

### Install a distribution
{% raw %}
```
wsl --install -d Ubuntu-24.04
```
{% endraw %}

### Get the WSL IP Address

{% raw %}
```
wsl ip -4 addr show eth0
```
{% endraw %}

or to get just the IP address cleanly,

{% raw %}
```
wsl ip -4 -o addr show eth0 | awk '{print $4}' | cut -d/ -f1
```
{% endraw %}

### Start WSL
{% raw %}
```
wsl
```
{% endraw %}

### Start a specific distro
{% raw %}
```
wsl -d Ubuntu-24.04
```
{% endraw %}

### Shutdown all WSL instances
{% raw %}
```
wsl --shutdown
```
{% endraw %}

### Terminate a specific distro
{% raw %}
```
wsl --terminate Ubuntu-24.04
```
{% endraw %}

### List installed distros
{% raw %}
```
wsl --list --verbose
```
{% endraw %}

### List available distros
{% raw %}
```
wsl --list --online
```
{% endraw %}

### Set default distro
{% raw %}
```
wsl --set-default Ubuntu-24.04
```
{% endraw %}

### Export a distro
{% raw %}
```
wsl --export Ubuntu-24.04 ubuntu-backup.tar
```
{% endraw %}

### Import a distro
{% raw %}
```
wsl --import Ubuntu-24.04 C:\WSL\Ubuntu ubuntu-backup.tar
```
{% endraw %}

### Delete a distro
{% raw %}
```
wsl --unregister Ubuntu-24.04
```
{% endraw %}

---

## 📝 Summary

WSL2 provides a powerful, lightweight Linux environment directly inside Windows. It is ideal for development, automation, scripting, and running tools like Python, Git, Docker, and Ansible. With Ubuntu 24.04, WSL2 becomes a flexible and efficient platform for both personal and professional workflows.