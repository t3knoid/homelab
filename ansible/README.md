# Ansible

https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html

## Virtual Machine Configuration

Ansible will be installed on a VM running a minimal Ubuntu 24 installation. A second disk will be used for the Ansible work folder mounted on /ansible.

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

### Create Ansible Group

Create the ansible group.

```bash
sudo addgroup ansible
```

Add users to the group.

```bash
sudo adduser frank ansible
```

## Ansible Installation

As of this writing, the latest version of Ansible is version [10.4.0](https://github.com/ansible-community/ansible-build-data/blob/main/10/CHANGELOG-v10.md#ansible-core) which contains ansible-core 2.17.4.


### Install Python

Install Python3 from Ubuntu repository.

```bash
sudo apt-get update
sudo apt-get install python3
```

#### Create a Python Virtual Environment

A Python virtual environment will be created to run Ansible. This will allow for side-by-side installations of different versions of Ansible.

#### Download the Python venv module

```bash
sudo apt-get update
sudo apt-get install python3.12-venv
```

#### Create and activate the virtual environment

Create a specific Python virtual environment allows the use of different versions of Ansible and Python combination in parallel. This is especially useful when testing new versions.

Notice the use of version numbers in the environment name for transparency.

```bash
cd /ansible
python3 -m venv python3.12.3_ansible10.4.0
```

Activate the environment with the following command.

```bash
source python3.12.3_ansible10.4.0/bin/activate
```

To deactivate this environment, simply run **deactivate**.

#### Make sure the latest version of pip is installed

```bash
pip install --upgrade pip setuptools
```

#### Use pip to install Ansible

```bash
pip install ansible
```

```bash
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

## Ansible Getting Started

Change to the Ansible working folder.

```bash
cd /ansible
```

Activate the environment with the following command.

```bash
source python3.12.3_ansible10.4.0/bin/activate
```

Initialize a new ansible.cfg

```bash
ansible-config init --disabled -t all > ansible.cfg
```

## References

- https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#installation-guide
- https://docs.ansible.com/ansible/latest/cli/ansible-config.html#ansible-config
- https://docs.ansible.com/ansible/latest/reference_appendices/config.html

## Semaphore

https://github.com/semaphoreui/semaphore

https://hub.docker.com/r/semaphoreui/semaphore

https://semaphoreui.com/install/docker/2_10_22/
