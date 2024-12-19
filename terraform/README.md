# Terraform

Terraform will be used to provision virtual machines.

## Installation

Terraform is installed using the Ansible playbook, playbooks/terraform/deploy_terraform.yml. This uses the roles/terraform_setup role.

The terraform_setup role, installs Terraform from a downloaded archive. The version of Terraform is controlled by the variable, **terraform_setup_version**. 

## Proxmox Integration

Proxmox is integrated with Terraform by using the [Telmate Proxmox Provider](https://registry.terraform.io/providers/Telmate/proxmox/latest/docs). The provider is configured to use token authentication to authenticate with Proxmox.

## Ansible Integration

Terraform is installed as part of the Ansible controller. Thus, its configuration file (main.tf) is installed in the default Ansible controller root working folder, /ansible/dev/ansible/.


