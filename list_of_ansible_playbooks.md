---
title: "List of Ansible Playbooks"
---

# List of Ansible Playbooks

## Provisioning a Virtual Machine

It is important to highlight provisioning a new virtual machine because it is core to deploying services. Running the [playbooks/provision_vm.yml](https://homelab.refol.us/projects/home-lab/repository/ansible/revisions/main/entry/playbooks/ansible/deploy_ansible.yml) playbook is unique in that it requires using the *ansible* become user.

{% raw %}
``` shell
cd /ansible/dev/ansible
git pull
INV=inventory/ansible/inventory.ini
ansible-playbook -k -i $INV playbooks/provision_vm.yml
```
{% endraw %}

When prompted for the become user password, make sure to enter the password for the *ansible* user.

Provisioning a new virtual machine using this playbook calls other playbooks that does the following:

* Create a new virtual machine
* Create required users
* Join the virtual machine to the domain
* Deploy Python3 to the virtual machine
* Prep Ansible node
* Formats second disk if available

## Ansible Playbooks

|Operation |Playbook |
|--|--|
| Provision a new virtual machine | [playbooks/provision_vm.yml](https://homelab.refol.us/projects/home-lab/repository/ansible/revisions/main/entry/playbooks/provision_vm.yml) |
| Deploy Code Server | [playbooks/deploy_code_server.yml](https://homelab.refol.us/projects/home-lab/repository/ansible/revisions/main/entry/playbooks/deploy_code_server.yml) |
| Create a new virtual machine | [playbooks/vms/create_vm.yml](https://homelab.refol.us/projects/home-lab/repository/ansible/revisions/main/entry/playbooks/vms/create_vm.yml) |
| Create users | [playbooks/vms/add_users.yml](https://homelab.refol.us/projects/home-lab/repository/ansible/revisions/main/entry/playbooks/vms/add_users.yml) |
| Join virtual machine to domain | [ad/join_domain.yml](https://homelab.refol.us/projects/home-lab/repository/ansible/revisions/main/entry/playbooks/ad/join_domain.yml) |
| Deploy Python3 | [python/deploy_python3.yml](https://homelab.refol.us/projects/home-lab/repository/ansible/revisions/main/entry/playbooks/python/deploy_python3.yml) |
| Prep Ansible node | [playbooks/ansible/prep_ansible_node.yml](https://homelab.refol.us/projects/home-lab/repository/ansible/revisions/main/entry/playbooks/ansible/prep_ansible_node.yml)
| Join a domain | [playbooks/ad/join_domain.yml](https://homelab.refol.us/projects/home-lab/repository/ansible/revisions/main/entry/playbooks/ad/join_domain.yml) |
| Prep disks | [playbooks/vms/prep_disk.yml](https://homelab.refol.us/projects/home-lab/repository/ansible/revisions/main/entry/playbooks/vms/prep_disk.yml) |
| Create a snapshot of a virtual machine | [playbooks/vms/create_vm_snaphsot.yml](https://homelab.refol.us/projects/home-lab/repository/ansible/revisions/main/entry/playbooks/vms/create_vm_snapshot.yml) |
| Remove a snapshot of a virtual machine | [playbooks/vms/remove_vm_snapshot.yml](https://homelab.refol.us/projects/home-lab/repository/ansible/revisions/main/entry/playbooks/vms/remove_vm_snapshot.yml) |
| Reboot a virtual machine  | [playbooks/vms/reboot_vm.yml](https://homelab.refol.us/projects/home-lab/repository/ansible/revisions/main/entry/playbooks/vms/reboot_vm.yml) |
| Shutdown a virtual machine  | [playbooks/vms/shutdown_vm.yml](https://homelab.refol.us/projects/home-lab/repository/ansible/revisions/main/entry/playbooks/vms/shutdown_vm.yml) |
| Stop a virtual machine  | [playbooks/vms/stop_vm.yml](https://homelab.refol.us/projects/home-lab/repository/ansible/revisions/main/entry/playbooks/vms/stop_vm.yml) |
| Start a virtual machine  | [playbooks/vms/start_vm.yml](https://homelab.refol.us/projects/home-lab/repository/ansible/revisions/main/entry/playbooks/vms/start_vm.yml) |
| Upgrade virtual machine operating system | [playbooks/vms/upgrade_vm_os.yml](https://homelab.refol.us/projects/home-lab/repository/ansible/revisions/main/entry/playbooks/vms/upgrade_vm_os.yml) |
| Create a virtual machine template | [playbooks/vms/create_template.yml](https://homelab.refol.us/projects/home-lab/repository/ansible/revisions/main/entry/playbooks/vms/create_template.yml) |
| Leave a domain | [playbooks/ad/leave_domain.yml](https://homelab.refol.us/projects/home-lab/repository/ansible/revisions/main/entry/playbooks/ad/leave_domain.yml) |
| Generate certificates | [playbooks/certs/generate_certs.yml](https://homelab.refol.us/projects/home-lab/repository/ansible/revisions/main/entry/playbooks/certs/generate_certs.yml) |
| Stage certificates | [playbooks/certs/stage_certs.yml](https://homelab.refol.us/projects/home-lab/repository/ansible/revisions/main/entry/playbooks/certs/stage_certs.yml) |
| Add a CNAME entry | [playbooks/dns/add_cname_entry.yml](https://homelab.refol.us/projects/home-lab/repository/ansible/revisions/main/entry/playbooks/dns/add_cname_entry.yml) |
| Add a DNS entry | [playbooks/dns/add_dns_entry.yml](https://homelab.refol.us/projects/home-lab/repository/ansible/revisions/main/entry/playbooks/dns/add_dns_entry.yml) |
| Delete a CNAME entry | [playbooks/dns/delete_cname_entry.yml](https://homelab.refol.us/projects/home-lab/repository/ansible/revisions/main/entry/playbooks/dns/delete_cname_entry.yml) |
| Delete a DNS entry | [playbooks/dns/delete_dns_entry.yml](https://homelab.refol.us/projects/home-lab/repository/ansible/revisions/main/entry/playbooks/dns/delete_dns_entry.yml) |
| Restart DNS service | [playbooks/dns/restart_dns.yml](https://homelab.refol.us/projects/home-lab/repository/ansible/revisions/main/entry/playbooks/dns/restart_dns.yml) |



