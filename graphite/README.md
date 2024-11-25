# Graphite

[Graphite](https://graphiteapp.org/) is one of the [Proxmox supported metric server](https://pve.proxmox.com/wiki/External_Metric_Server).

## Installation

Graphite is installed in an Ubuntu virtual machine using the disparate installation guide located in https://graphite.readthedocs.io/en/latest/install.html. The installation uses pip to install the three graphite packages, Whisper, Carbon, and Graphite Web. 

## Ansible Playbook

The Ansible playbook playbooks/graphite/deploy_graphite.yml can be used to deploy the Graphite suite into a given inventory. The graphite_setup role performs the bulk of the Graphite installation. This includes setting up Python, Postgresql and Nginx.

### Python Environment

The Python environment is configured in /opt/graphite. The Ansible tasks is based on the [Installing in Virtualenv](https://graphite.readthedocs.io/en/latest/install-virtualenv.html) section of the documentation.

### Whisper

Whisper is the database backend that uses Postgresql. After installation, it must be primed as noted in the [Webapp Database Setup](https://graphite.readthedocs.io/en/latest/config-database-setup.html) section of the documentation. The roles/graphite_setup/tasks/whisper.yml file contains the tasks to configure Whisper.

### Graphite-Web

Graphite-web is Graphite's front-end using [nginx + gunicorn](https://graphite.readthedocs.io/en/latest/config-webapp.html#nginx-gunicorn). It is configured as noted in the [Configuring the Webapp](https://graphite.readthedocs.io/en/latest/config-webapp.html) section of the documentation. The roles/graphite_setup/tasks/webapp.yml file contains the tasks to configure Graphite-web. The Graphite web process is managed using systemd.

```bash
systemctl started graphite-web.service
```

#### Bug
One caveat with the Graphite-web is an apparent [bug](https://serverfault.com/questions/364185/ldap-authentication-with-graphite
) in the [authenticate method](https://github.com/graphite-project/graphite-web/blob/master/webapp/graphite/account/ldapBackend.py). 

### Carbon

The [Carbon daemons](https://graphite.readthedocs.io/en/latest/carbon-daemons.html) is what listens and processes incoming data from external sources. Only carbon-cache.py is activated.

## Configuration

Graphite is configured using the [local_settings.py](https://graphite.readthedocs.io/en/latest/config-local-settings.html) file. This file is deployed in Ansible using the roles/graphite_setup/templates/local_settings.py.j2 template 

## LDAP Authentication

LDAP is used to authenticate to the Active Directory server (ad0). THe following Ansible variables are used to configure LDAP.

```yaml
graphite_setup_ldap_server: "192.168.2.251"
graphite_setup_ldap_port: 389
graphite_setup_ldap_use_tls: "False"
graphite_setup_ldap_uri: ldap://192.168.2.251
graphite_setup_ldap_search_base: "CN=Users,DC=refol,DC=us"
graphite_setup_ldap_base_user: "CN=LDAP Bind User,OU=Service Accounts,DC=refol,DC=us"
# graphite_setup_ldap_base_pass: See vault
graphite_setup_ldap_user_query: "(sAMAccountName=%s)"
graphite_setup_ldap_user_dn_template: "CN=%(username)s,CN=Users,DC=refol,DC=us"
```

## Troubleshooting

Use journalctl to tail graphite-web.service debug output.

```bash
journalctl -f -u graphite-web.service
```
Log files are located in 
- /opt/graphite/storage/log
- /opt/var/log/nginx
- /var/log/postgresql/postgresql-17-main.log

## References

- https://graphite.readthedocs.io/en/latest/install-pip.html
