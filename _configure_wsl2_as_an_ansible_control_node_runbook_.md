---
title: "Configure WSL2 as an Ansible Control Node Runbook"
---

# 🧰 Configure WSL2 as an Ansible Control Node Runbook 

## 🎯 Purpose
Provision **WSL2 (Ubuntu 24.04)** on a Windows workstation and configure it as an **Ansible control node** capable of managing Linux and Windows hosts.

---

## 🧩 Prerequisites

- Windows 11 workstation  
- Administrator access  
- Virtualization enabled  
- Pi‑hole or equivalent DNS (optional but recommended)  
- Existing Ansible control node (for remote configuration steps)

---

## 🏗️ Install WSL2

### Steps
- Open **PowerShell as Administrator**  
- Install Ubuntu 24.04:

  ```powershell
  wsl --install -d Ubuntu-24.04
  ```

- When prompted:
  - Set default user to **ansible**
  - Set password

> [!IMPORTANT]  
> The `ansible` user is required for automated configuration.

- Reboot if prompted

### Optional — Change Default User Later
{% raw %}
```powershell
ubuntu config --default-user <username>
wsl --shutdown
wsl -d Ubuntu-24.04
```
{% endraw %}

---

## 🚀 Launch WSL2

### Steps
- Open Windows Terminal  
- Start Ubuntu:

  ```bash
  wsl -d Ubuntu-24.04
  ```

---

## 🔄 Update Linux Packages

### Steps
Run:

{% raw %}
```bash
sudo apt update && sudo apt upgrade -y
```
{% endraw %}

---

## 🔐 Configure Passwordless Sudo

### Steps
- Create sudoers file:

  ```bash
  sudo vi /etc/sudoers.d/99_ansible
  ```

- Add:

  ```text
  %ansible ALL=(ALL) NOPASSWD:ALL
  ```

- Save and exit

---

## 🏷️ Set WSL Hostname

### Steps
- Edit config:

  ```bash
  sudo vi /etc/wsl.conf
  ```

- Add:

  ```ini
  [network]
  hostname = dev-0
  generateHosts = false
  ```

- From Windows PowerShell:

  ```powershell
  wsl --shutdown
  ```

- Restart WSL

---

## 🔐 Enable External SSH Access

### Get WSL IP Address
{% raw %}
```powershell
wsl ip -4 -o addr show eth0 | awk '{print $4}' | cut -d/ -f1
```
{% endraw %}

### Configure Port Forwarding
Replace `wsl_ip_address`:

{% raw %}
```powershell
netsh interface portproxy add v4tov4 listenport=22 listenaddress=0.0.0.0 connectport=22 connectaddress=wsl_ip_address
```
{% endraw %}

> [!IMPORTANT]  
> SSH should now be reachable using the **Windows host IP**.

---

## 🌐 Add Host to DNS (Pi‑hole)

### Steps
- Open Pi‑hole → **Settings → Local DNS Records**  
- Add:
  - **Domain:** WSL hostname (e.g., `dev-0`)
  - **IP:** Windows host IP  
- Save record

### Verify
{% raw %}
```bash
nslookup dev-0
```
{% endraw %}

---

## ⚙️ Update Ansible Inventory

### Add to `global_ip_addresses`
Edit `roles/global/vars/main.yml`:

{% raw %}
```yaml
global_ip_addresses:
  dev-0: 192.168.2.120
```
{% endraw %}

### Add to Inventory Group
Edit `inventory/ansible/inventory.ini`:

{% raw %}
```
[wsl]
dev-0
```
{% endraw %}

---

## 🛠️ Configure WSL Host Using Ansible

> [!IMPORTANT]  
> Confirm SSH access to the WSL host using the Windows host IP.

### Bootstrap Python 3
{% raw %}
```bash
ansible-playbook -k -i inventory/ansible/inventory.ini playbooks/python/bootstrap_python3.yml -u ansible -l dev-0
```
{% endraw %}

### Join Active Directory Domain
{% raw %}
```bash
ansible-playbook -k -i inventory/ansible/inventory.ini playbooks/ad/join_domain.yml -u ansible -l dev-0
```
{% endraw %}

> [!WARNING]  
> This playbook reboots WSL.  
> After reboot:  
> - Start WSL manually  
> - Reconfigure Windows port forwarding  

### Prep Ansible Node
{% raw %}
```bash
ansible-playbook -k -i inventory/ansible/inventory.ini playbooks/ansible/prep_ansible_node.yml -u ansible -l dev-0
```
{% endraw %}

### Deploy Ansible
{% raw %}
```bash
ansible-playbook -k -i inventory/ansible/inventory.ini playbooks/ansible/deploy_ansible.yml -u ansible -l dev-0
```
{% endraw %}

---

## 🔍 Verify Ansible Installation

### Steps
- Activate Python environment:

  ```bash
  source /opt/python3.12/bin/activate
  ```

- Check version:

  ```bash
  ansible --version
  ```

### Expected Output (Example)
{% raw %}
```
ansible [core 2.19.5]
ansible python module location = /opt/python_3.12/lib/python3.12/site-packages/ansible
python version = 3.12.3
...
```
{% endraw %}

---

## 📁 Working With Repositories

### Option A — Use Windows Repo
{% raw %}
```bash
cd /mnt/c/Users/<username>/GitHub/<repo>
```
{% endraw %}

### Option B — Clone Into WSL (Recommended)
{% raw %}
```bash
git clone https://github.com/<your-repo> ~/projects/<repo>
```
{% endraw %}

**Benefits**

- Faster filesystem performance  
- Avoids CRLF issues  
- Cleaner environment separation  

---

## 🖥️ VS Code Integration (WSL)

### Steps
- Install **WSL** extension in VS Code  
- Open repo  
- Open **Remote Explorer → WSL Targets**  
- Select `Ubuntu-24.04`  
- Click **Open Folder**  

VS Code now uses:

- WSL Python interpreter  
- WSL Ansible extension  
- WSL linting and execution  

