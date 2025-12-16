---
title: "Configuring an Ansible Control Node"
---

# Configuring an Ansible Control Node

The following are steps in configuring an Ansible control node. These steps have been automated using an [Ansible playbook](https://homelab.refol.us/projects/home-lab/repository/ansible/revisions/main/entry/playbooks/ansible/deploy_ansible.yml).

### Adding Second Drive

1. Add a new disk from the Proxmox web GUI.
2. Boot the VM.
3. Enumerate the new disk device using fdisk -l.
4. Use fdisk to create a new partition.
5. Format the new disk using mkfs (e.g., sudo mkfs -t ext4 /dev/vdb1)
6. Create mounpoint /ansible (e.g. sudo mkdir /ansible).
7. Configure /etc/fstab with new mountpoint (e.g., add the line `/dev/vdb1       /ansible        ext4    defaults        0       2`)
8. Mount the disk to mountpoint (e.g., sudo mount /ansible).
9. Execute the following chmod command to allow full group access `sudo chmod -R g+rwx /ansible`.

### Join Machine to Active Directory

The [Join an Ubuntu 24.04 VM to Active Directory Domain](../activedirectory/join_an_ubuntu_24.04_to_active_directory_domain.md) document provides instructions on how to join the machine to active directory.

### Configure Ansible Become User

To provide some semblance of security, use a non-root user as the become_user. The Active Directory user ansible@refol.us will be used. 

#### Create Ansible Active Directory User

Create an active directory user that will be used as the Ansible privileged user.

```powershell
New-ADUser -Name "Ansible" -GivenName "Ansible" -Surname "User" -SamAccountName "ansible" -UserPrincipalName "ansible@refol.us" -AccountPassword(Read-Host -AsSecureString "Input Password") -Enabled $true
```

Enter a password when prompted.

#### Give the **ansible** domain user permission in the Proxmox cluster.

From the Proxmox select **Datacenter > Permissions > Users**. Click **Add**. Add *ansible* in the User name field.

> [!IMPORTANT] 
> The active directory, refol.us, must be added as a Realm in Proxmox before the ansible user can be added. Open **Datacenter > Permissions > Realms > Add > Active Directory Server** to add an active directory realm.

#### Create a Proxmox API Token

The API token will be used by Ansible when performing API calls on the Proxmox server. Select **Datacenter > Permissions > API Tokens > Add**. Enter 

User: ansible@refol.us
Token ID: ansible_become_user

Click **Add** when done. The Token Secret will be shown. Copy the Token ID and Secret values.

#### Create the ansible group.

Execute the following from the ansible control node.

``` shell
sudo addgroup ansible
```

#### Add the ansible@refol.us to the ansible group.

Execute the following from the ansible control node.

``` shell
sudo usermod -a -G ansible ansible@refol.us
```

``` shell
sudo usermod -a -G ansible ansible
```

Add ansible@refol.us to the sudo group.

``` shell
sudo usermod -a -G sudo ansible@refol.us
```

``` shell
sudo usermod -a -G sudo ansible
```

The following must be configured in Ansible when elevating Ansible to use root access.

``` shell
become: true
become_user: ansible
become_method: sudo
```

## Ansible Installation

As of this writing, the latest version of Ansible is version [10.4.0](https://github.com/ansible-community/ansible-build-data/blob/main/10/CHANGELOG-v10.md#ansible-core) which contains ansible-core 2.17.4.

### Install Python

Install Python3 from Ubuntu repository.

``` shell
sudo apt-get update
sudo apt-get install python3
```

#### Create a Python Virtual Environment

A Python virtual environment will be created to run Ansible. This will allow for side-by-side installations of different versions of Ansible.

#### Download the Python venv module

``` shell
sudo apt-get update
sudo apt-get install python3.12-venv
```

#### Create and activate the virtual environment

Create a specific Python virtual environment allows the use of different versions of Ansible and Python combination in parallel. This is especially useful when testing new versions.

Notice the use of version numbers in the environment name for transparency.

``` shell
cd /ansible
python3 -m venv python3.12.3_ansible10.4.0
```

Activate the environment with the following command.

``` shell
source python3.12.3_ansible10.4.0/bin/activate
```

To deactivate this environment, simply run **deactivate**.

#### Make sure the latest version of pip is installed

``` shell
pip install --upgrade pip setuptools
```

#### Use pip to install Ansible

``` shell
pip install ansible
```

``` shell
ansible --version
ansible [core 2.17.4]
  config file = None
  configured module search path = ['/home/frank@refol.us/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules']
  ansible python module location = /ansible/python3.12.3_ansible10.4.0/lib/python3.12/site-packages/ansible
  ansible collection location = /home/frank@refol.us/.ansible/collections:/usr/share/ansible/collections
  executable location = /ansible/python3.12.3_ansible10.4.0/bin/ansible
  python version = 3.12.3 (main, Sep 11 2024, 14:17:37) [GCC 13.2.0] (/ansible/python3.12.3_ansible10.4.0/bin/python3)
  jinja version = 3.1.4
  libyaml = True
```

### Install Python Modules

#### proxmoxer

``` shell
python -m pip install proxmoxer
```

#### requests

``` shell
python -m pip install requests
```

#### pycdlib

``` shell
python -m pip install pycdlib
```

### Other Installations

``` shell
sudo apt install sshpass acl
```

## Ansible Getting Started

### Activate Working Environment

Change to the Ansible working folder.

``` shell
cd /ansible/dev
```

Activate the environment with the following command.

``` shell
source ../python3.12.3_ansible10.4.0/bin/activate
```

### Create Ansible.cfg

Initialize a new ansible.cfg

``` shell
ansible-config init --disabled -t all > ansible.cfg
```

### Set the Vault Password File 

Create a ~/.vault_pass.txt file. Add vault passwords in this file. Edit ansible.cfg to set the **vault_password_file** setting to the path to this file.

``` shell
vault_password_file=~/.vault_pass.txt
```

## Configure SSH Access to Proxmox Servers

Since we are using Proxmox as the VM provider, the Ansible account used to execute playbooks must be configured to access each Proxmox node via SSH.

``` shell
ssh pve-0
ssh pve-1
ssh pve-2
```

Similarly, ensure that the become_root user (i.e., ansible@refol.us) has access as well.

``` shell
ssh ansible@pve-0
ssh ansible@pve-1
ssh ansible@pve-2
```

Test the become user setting using the following command. Note this command assumes that the specified inventory is available where the ansible host has been defined.

``` shell
ansible pvenodes -i inventory/pve/inventory.ini -m ping --user=ansible -k
```

Enter the ansible user password when prompted.


## Ansible Lint

``` shell
pip3 install ansible-lint
```

## References

- https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#installation-guide
- https://docs.ansible.com/ansible/latest/cli/ansible-config.html#ansible-config
- https://docs.ansible.com/ansible/latest/reference_appendices/config.html
- https://ansible.readthedocs.io/projects/lint/installing/
- https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html

