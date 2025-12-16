# Terraform

HashiCorp [Terraform](https://developer.hashicorp.com/terraform/intro) is an infrastructure as code (IaC) tool similar to Ansible that lets you define network resources in human-readable configuration files. In this home lab, it is used to provision virtual machines from the Proxmox Virtual Environment.

## Integration with Ansible

When I initially started automating my home lab, I used [Ansible to provision virtual machines](https://homelab.refol.us/projects/home-lab/repository/ansible/revisions/main/entry/roles/vms/tasks/provision.yml). In time, I migrated to using Terraform for provisioning virtual machines in order to get exposure to using its technology. I want to have a seamless integration with Ansible since that is the primary interface to provision virtual machines. To achieve this, I've created a separate task file that mirrors what the existing provision.yml task file in the [vm role](https://homelab.refol.us/projects/home-lab/repository/ansible/revisions/main/show/roles/vms) does. This task file dynamically creates the necessary Terraform config files and performs the Terraform command to provision the target host.

## HashiCorp Vault

Another opportunity to learn a new technology is using [[HashiCorp Vault]] to keep secrets used in deploying virtual machines. The current Ansible tasks use Ansible's vault. In time, I will probably use HashiCorp Vault for all secrets used in Ansible playbooks.

