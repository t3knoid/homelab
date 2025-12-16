# ⚙️ Ansible

Ansible is the automation framework used to manage virtual machine operations across the homelab environment. It provides:

- **Provisioning** of new virtual machines  
- **Deployment** of required applications  
- **Configuration management** of applications whenever possible  

By leveraging Ansible, infrastructure tasks become streamlined, repeatable, and highly maintainable.  
A curated [List of Ansible Playbooks](list_of_ansible_playbooks.md) supports standardized workflows across the environment. 

Each Ansible playbook includes its own `README.md` for documentation. A consolidated [Playbook Index](https://homelab.refol.us/projects/home-lab/repository/ansible/revisions/main/entry/playbooks/README.md) is available in the `playbooks/` root folder. The documentation process is explained in the [Ansible Playbook Documentation Workflow](ansible_playbook_documentation_workflow.md) page.

Each Ansible role includes its own `README.md` for documentation. A consolidated [Role Index](https://homelab.refol.us/projects/home-lab/repository/ansible/revisions/main/entry/roles/README.md) is available in the `roles/` root folder. The documentation process is explained in the [Ansible Role Documentation Workflow](ansible_role_documentation_workflow.md) page.

---

## 🗂 Documentation Map
- [Quick-Start Checklist](Ansible_Quick‑Start_Checklist)  
- [Directory Structure & Conventions](Ansible_Directory_Structure_&_Conventions)  
- [Semaphore](../Semaphore)  

---

## 🔑 Privileged Execution (Become User)

Ansible employs a dedicated account for privilege escalation:

- The local account **ansible** is typically used during VM provisioning.  
- After provisioning, any user in the domain group **ansible** can elevate privileges to run Ansible commands securely.  

This model enforces controlled access while maintaining operational flexibility.

---

## 🖥 Control Nodes

Two [Ansible control nodes](https://homelab.refol.us/projects/home-lab/repository/ansible/revisions/main/entry/inventory/ansible/inventory.ini) are defined to orchestrate automation tasks.

### Working on a Control Node
After connecting to a control node (e.g., via SSH), initialize your environment with:

```shell
source /opt/python_3.12/bin/activate
cd ~/ansible
git pull
```

This ensures you are operating with the latest codebase and dependencies.  
For details on repository organization, see [Directory Structure & Conventions](./ansible-directory-structure.md).

💡 Playbooks can also be executed through [Semaphore UI](Semaphore), a web-based interface that provides a dashboard for managing inventories, credentials, and runs—ideal if you prefer not to work directly from the console.

### Deploying or Updating Ansible
To deploy or update Ansible on a control node:

```shell
INV=inventory/ansible/inventory.ini
ansible-playbook -k -i $INV playbooks/ansible/deploy_ansible.yml
```

This playbook automates installation and configuration, keeping control nodes consistent and up to date.

---

## 📚 Documentation Workflows

Automated scripts generate Markdown documentation whenever changes are made, ensuring playbooks and roles remain self‑documenting and contributor‑friendly:

- **[Ansible Role Documentation Workflow](ansible_role_documentation_workflow.md)**  
  Enforces mandatory metadata in each role and builds role‑level READMEs plus a global index.

- **[Ansible Playbook Documentation Workflow](ansible_playbook_documentation_workflow.md)**  
  Enforces mandatory `# Purpose:` comments, generates per‑playbook READMEs, builds folder‑level summaries, and maintains the global playbook index.

These workflows provide contributor guidance, examples of generated outputs, and expectations for adding new roles or playbooks.

---

## 🚀 Quick-Start Checklist

For a fast onboarding guide with essential commands and common playbooks, see the [Ansible Quick-Start Checklist](Ansible_Quick‑Start_Checklist).