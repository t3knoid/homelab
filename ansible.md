---
title: "️ Ansible"
---

# ⚙️ Ansible

Ansible is the automation framework used to manage virtual machine operations across the homelab environment. It enables:

* **[Provisioning](automated_virtual_machine_provisioning.md)** of new virtual machines
* **Deployment** of required applications
* **Configuration management** of applications wherever possible

By leveraging Ansible, infrastructure tasks become **streamlined, repeatable, and maintainable**.

---

## 🗂 Core Concepts

### Playbooks

Each playbook defines a set of automation tasks and includes its own `README.md`.
A consolidated [Playbook Index](https://github.com/t3knoid/ansible/blob/main/playbooks/README.md) is available in the `playbooks/` folder.

### Roles

Roles modularize playbooks into reusable components and include their own `README.md`.
A consolidated [Role Index](https://github.com/t3knoid/ansible/blob/main/roles/README.md) is available in the `roles/` folder.

### Inventories

Inventories define the hosts and groups targeted by playbooks and include their own `README.md`.
A consolidated [Inventory Index](https://github.com/t3knoid/ansible/blob/main/inventory/README.md) is available in the `inventory/` folder.

💡 For **all documentation workflows**, see [Documenting Ansible](documenting_ansible.md).

---

## 🔑 Privileged Execution (Become User)

Ansible uses a controlled privilege model:

* The local account **ansible** is typically used during VM provisioning.
* After provisioning, any user in the domain group **ansible** can elevate privileges to run Ansible commands securely.

This ensures **controlled access** while maintaining operational flexibility.

---

## 🖥 Control Nodes

Two [Ansible control nodes](https://github.com/t3knoid/ansible/blob/main/inventory/ansible/inventory.ini) orchestrate automation tasks.

For a complete guide on configuring an Ansible node, 
👉 see [Configuring an Ansible Control Node](configuring_an_ansible_control_node.md)
 
### Working on a Control Node

After connecting (e.g., via SSH), initialize your environment:

{% raw %}
```shell
source /opt/python_3.12/bin/activate
cd ~/ansible
git pull
```
{% endraw %}

This ensures you are working with the **latest codebase and dependencies**. For repository organization, 

👉 see [Ansible Directory Structure & Conventions](ansible_directory_structure_&_conventions.md).

💡 **Tip:** Playbooks can also be executed through [Semaphore UI](semaphore.md), a web interface for managing inventories, credentials, and runs.

### Deploying or Updating Ansible

To install or update Ansible on a control node:

{% raw %}
```shell
INV=inventory/ansible/inventory.ini
ansible-playbook -k -i $INV playbooks/ansible/deploy_ansible.yml
```
{% endraw %}

This keeps control nodes **consistent and up to date**.

---

## 🗂 Documentation Map

* [Ansible Quick-Start Checklist](ansible_quick-start_checklist.md) - For onboarding with essential commands and common playbooks
* [Ansible Directory Structure & Conventions](ansible_directory_structure_&_conventions.md) - provides a detailed reference for the organization of the Ansible repository
* [Semaphore](semaphore.md) - is a lightweight web interface for managing and executing Ansible playbooks
* [Documenting Ansible](documenting_ansible.md) – guides for contributing and generating playbook, role, and inventory documentation