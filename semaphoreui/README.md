# Semaphore UI

[Semaphore UI](https://semaphoreui.com/install/) is a web application that provides a user interface simplifies Ansible playbook execution.

# Installation

Semaphore UI is installed in an Ubuntu virtual machine using [Ubuntu's package manager](https://docs.semaphoreui.com/administration-guide/installation/package-manager/). During installation a default admin user is created. The initial admin password is written into a file located in the config folder. 

The Semaphore UI systemd service is executed using an [active directory account](#service-account). This account must be manually created.

## Configuration

The configuration folder is located in */ansible/semaphore*. The configuration file is located in */ansible/semaphore/etc/config.json*.

### Python

A Python environment is used to execute Semaphore UI's service.

### Database

PostreSQL is used for the Semaphore UI backend database. The database is installed in the same host as the Semaphore service. The database data folder is located in */ansible/pgdata*. The following configuration is used to configure PostgreSQL.

``` json
  "postgres": {
    "host": "192.168.2.102",
    "name": "semaphoreui",
    "user": "semaphoreui",
    "pass": "*****"
  },
  "dialect": "postgres",
```

### LDAP

[LDAP](https://docs.semaphoreui.com/administration-guide/ldap/) is used to authenticate users into Semaphore UI. The following configuration is used to configure LDAP.

``` json
  "ldap_enable": true,
  "ldap_needtls": false,
  "ldap_binddn": "CN=LDAP Bind User,OU=Service Accounts,DC=refol,DC=us",
  "ldap_bindpassword": "*****",
  "ldap_server": "ad0.refol.us:389",
  "ldap_searchdn": "CN=Users,DC=refol,DC=us",
  "ldap_searchfilter": "(sAMAccountName=%s)",
  "ldap_mappings": {
    "dn": "",
    "mail": "userPrincipalName",
    "uid": "sAMAccountName",
    "cn": "cn"
  },

```

## Systemd Service

Semaphore UI is executed automatically using a Systemd service.

The following shows the systemd service unit file content created during installation (i.e., /etc/systemd/system/semaphore.service).

``` ini
[Unit]
Description=Semaphore Ansible
Documentation=https://docs.semaphoreui.com
Wants=network-online.target
After=network-online.target
ConditionPathExists=/usr/bin/semaphore
ConditionPathExists=/ansible/semaphore/etc/config.json

[Service]
User=semaphore
Group=ansible
ExecReload=/bin/kill -HUP $MAINPID
ExecStart=/bin/bash -c 'source /opt/python_3.12/bin/activate && /usr/bin/semaphore server --config=/ansible/semaphore/etc/config.json'
SyslogIdentifier=semaphore
Restart=always
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

Note the use of the user *semaphore* and Group *ansible* and the use of a Python virtual environment to execute the service.

## Service Account

A service account must be created in active directory and will be used to execute the Semaphore UI service. The following powershell command is used to create the active directory account.

``` powershell
New-ADUser -Name "Semaphore" -GivenName "Semaphore" -Surname "User" -SamAccountName "semaphore" -UserPrincipalName "semaphore@refol.us" -AccountPassword(Read-Host -AsSecureString "Input Password") -Enabled $true
```

## Web Host

The Semaphore UI from the URL https://semaphore.refol.us. Nginx is used as a reverse proxy to expose the Semaphore UI web host to the internet. A Let's Encrypt certificate is generated using [certbot](../certbot/README.md).

## Troubleshooting

Semaphore does not have a log file. Instead, all output is sent to system messages. These messages can be viewed using **journalctl**. The following command tails the journalctl output containing messages from the semaphore service.

``` shell
sudo journalctl -u semaphore -f
```

## Ansible Playbook

Ansible can be used to deploy Semaphore UI.

### Provision an Ubuntu VM

Ubuntu is used to host Semaphore UI. After configuring an appropriate inventory file (e.g., inventory/ansible/group_vars/all/main.yml), the following can be used to provision a new virtual machine running Ubuntu.

``` shell
ansible-playbook -u ansible -k -i inventory/ansible/inventory.ini playbooks/provision_vm.yml -l ansible-1
```

Note a limit is used to create the specific virtual machine that will host Semaphore UI.

### Deploying Semaphore UI

Semaphore UI can be deployed using an Ansible playbook. The host use is part of the ansible inventory (e.g., ansible-1).

``` shell
ansible-playbook -k -i inventory/ansible/inventory.ini playbooks/deploy_semaphoreui.yml
```

The playbook uses the *postgresql_setup* role to configure PostgreSQL. It also installs and configures Python and the Ansible Python module and other required modules.

### Configure Reverse Proxy

A reverse proxy is use to connect the Semaphore UI web host to the internet. A separate playbook is executed in order to configure the reverse proxy settings.

``` shell
ansible-playbook -k -i inventory/ansible/inventory.ini playbooks/rproxy/config_rproxy.yml
```

### Web Certificates

To generate web certificates for Semaphore, execute the following playbook.

``` shell
ansible-playbook -k -i inventory/ansible/inventory.ini playbooks/certs/generate_certs.yml
```

Stage the certificates for use by the reverse proxy using the following playbook.

``` shell
ansible-playbook -k -i inventory/ansible/inventory.ini playbooks/certs/stage_certs.yml
```

## Database Backup

Execute the following playbook to backup the Postgresql database.

``` shell
ansible-playbook -k -i inventory/ansible/inventory.ini playbooks/semaphoreui/backup_db.yml
```

This playbook uses pg_dump to create a backup located in /nfs/backups/. THe backup file is named with a "semaphoreui_" prefix followed by the date of the backup. The /nfs/backups mountpoint is a share from the Synology NAS.

## Using Semaphore

After successfully deploying Semaphore, login as **admin** to https://semaphore.refol.us. The setup generated password is located in /ansible/semaphore/.admin. After logging in, create a project. 

### Minimum Requirements

In order to configure tasks in a project, the following must be configured.

- Ansible repository - add the Ansible repository, https://github.com/t3knoid/ansible.git. Use the main branch and set the Access key to none.
- Key Store - Create two *Login with password* keys, the vault password and the Semaphore user credentials. 

### Tasks Templates and Inventory

Tasks templates is equivalent to commands and parameters needed to execute an Ansible playbook. A Task Template requires an Inventory to be specified.

#### Inventory

To create an Inventory specify the following:
- Name
- User Credentials - choose the Semaphore user credentials from the key store.
- Sudo Credentials - do not set.
- Type - Choose a File type and enter a path relative to the root of the ansible inventory (e.g. inventory/ansible/inventory.ini). Do not set the Repository field.

#### Task Template

For a task, specify the following:
- Name
- Path to playbook file - enter a path relative to the root of the ansible inventory (e.g. playbooks/linux/check_connection.yml)
- Inventory - Choose an inventory. An inventory must be created before it can be selected.
- Repository - Choose the configured ansible repository.
- Variable Group - Set to Empty.
- CLI args - Add -k.
- Vaults - Add the vault password configured in the key store.


