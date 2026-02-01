---
title: "️ Configuring an Ansible Control Node"
---

# 🖥️ Configuring an Ansible Control Node

The following steps describe how to configure an Ansible control node. These steps have been automated using the [Ansible deployment playbook](https://github.com/t3knoid/ansible/blob/main/docs/playbooks/deploy_ansible.md).

---

# 💽 Adding a Second Drive

1. Add a new disk from the Proxmox web GUI.  
2. Boot the VM.  
3. Enumerate the new disk using `fdisk -l`.  
4. Use `fdisk` to create a new partition.  
5. Format the new partition (e.g., `sudo mkfs -t ext4 /dev/vdb1`).  
6. Create the mount point `/ansible` (e.g., `sudo mkdir /ansible`).  
7. Add the new mount point to `/etc/fstab` (e.g.,  
   `/dev/vdb1  /ansible  ext4  defaults  0  2`).  
8. Mount the disk (e.g., `sudo mount /ansible`).  
9. Grant full group access:  
   `sudo chmod -R g+rwx /ansible`.

---

# 🏢 Joining the Machine to Active Directory

See the guide:  
**`[Looks like the result wasn't safe to show. Let's switch things up and try something else!]`**

---

# 🔐 Configure the Ansible Become User

Use a non‑root user for privilege escalation. The Active Directory user `ansible@refol.us` will serve as the Ansible become user.

## Create the Ansible Active Directory User

{% raw %}
```powershell
New-ADUser -Name "Ansible" -GivenName "Ansible" -Surname "User" -SamAccountName "ansible" -UserPrincipalName "ansible@refol.us" -AccountPassword(Read-Host -AsSecureString "Input Password") -Enabled $true
```
{% endraw %}

Enter a password when prompted.

## Grant Proxmox Permissions to the ansible User

In Proxmox:

**Datacenter → Permissions → Users → Add**  
Add the user **ansible**.

> ❗**IMPORTANT**
> The Active Directory domain `refol.us` must be added as a Realm before adding the user.  
> Navigate to **Datacenter → Permissions → Realms → Add → Active Directory Server**.

## Create a Proxmox API Token

This token will be used by Ansible for API calls.

**Datacenter → Permissions → API Tokens → Add**

- **User:** `ansible@refol.us`  
- **Token ID:** `ansible_become_user`

Click **Add**, then copy the Token ID and Secret.

## Create the ansible Group

{% raw %}
```shell
sudo addgroup ansible
```
{% endraw %}

## Add ansible@refol.us to the ansible Group

{% raw %}
```shell
sudo usermod -a -G ansible ansible@refol.us
sudo usermod -a -G ansible ansible
```
{% endraw %}

## Add ansible@refol.us to the sudo Group

{% raw %}
```shell
sudo usermod -a -G sudo ansible@refol.us
sudo usermod -a -G sudo ansible
```
{% endraw %}

## Configure Ansible Become Settings

{% raw %}
```yaml
become: true
become_user: ansible
become_method: sudo
```
{% endraw %}

---

# 📦 Ansible Installation

As of this writing, the latest version is **Ansible 10.4.0**, which includes **ansible-core 2.17.4**.

## Install Python

{% raw %}
```shell
sudo apt-get update
sudo apt-get install python3
```
{% endraw %}

## Create a Python Virtual Environment

A virtual environment allows multiple Ansible versions to coexist.

### Install the venv Module

{% raw %}
```shell
sudo apt-get update
sudo apt-get install python3.12-venv
```
{% endraw %}

### Create and Activate the Virtual Environment

{% raw %}
```shell
cd /ansible
python3 -m venv python3.12.3_ansible10.4.0
source python3.12.3_ansible10.4.0/bin/activate
```
{% endraw %}

Deactivate with:

{% raw %}
```shell
deactivate
```
{% endraw %}

### Upgrade pip

{% raw %}
```shell
pip install --upgrade pip setuptools
```
{% endraw %}

### Install Ansible

{% raw %}
```shell
pip install ansible
```
{% endraw %}

Verify installation:

{% raw %}
```shell
ansible --version
```
{% endraw %}

(Version output omitted for brevity.)

---

# 📚 Install Python Modules

## proxmoxer

{% raw %}
```shell
python -m pip install proxmoxer
```
{% endraw %}

## requests

{% raw %}
```shell
python -m pip install requests
```
{% endraw %}

## pycdlib

{% raw %}
```shell
python -m pip install pycdlib
```
{% endraw %}

## Other Required Packages

{% raw %}
```shell
sudo apt install sshpass acl
```
{% endraw %}

---

# 🚀 Getting Started with Ansible

## Activate the Working Environment

{% raw %}
```shell
cd /ansible/dev
source ../python3.12.3_ansible10.4.0/bin/activate
```
{% endraw %}

## Create ansible.cfg

{% raw %}
```shell
ansible-config init --disabled -t all > ansible.cfg
```
{% endraw %}

## Configure the Vault Password File

Create `~/.vault_pass.txt` and add your vault password.

In `ansible.cfg`:

{% raw %}
```ini
vault_password_file=~/.vault_pass.txt
```
{% endraw %}

---

# 🔑 Configure SSH Access to Proxmox Servers

Ensure the Ansible account can SSH into each Proxmox node:

{% raw %}
```shell
ssh pve-0
ssh pve-1
ssh pve-2
```
{% endraw %}

Ensure the become user can also connect:

{% raw %}
```shell
ssh ansible@pve-0
ssh ansible@pve-1
ssh ansible@pve-2
```
{% endraw %}

Test connectivity:

{% raw %}
```shell
ansible pvenodes -i inventory/pve/inventory.ini -m ping --user=ansible -k
```
{% endraw %}

Enter the password when prompted.

---

# 🧹 Ansible Lint

{% raw %}
```shell
pip3 install ansible-lint
```
{% endraw %}

---

# 📖 References

- [https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)  
- `https://docs.ansible.com/ansible/latest/cli/ansible-config.html` [(docs.ansible.com in Bing)](https://www.bing.com/search?q="https%3A%2F%2Fdocs.ansible.com%2Fansible%2Flatest%2Fcli%2Fansible-config.html")  
- [https://docs.ansible.com/ansible/latest/reference_appendices/config.html](https://docs.ansible.com/ansible/latest/reference_appendices/config.html)  
- [https://ansible.readthedocs.io/projects/lint/installing/](https://ansible.readthedocs.io/projects/lint/installing/)  
- [https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)