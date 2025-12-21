---
title: "Ansible Quick‑Start Checklist"
---

# Ansible Quick‑Start Checklist

This page provides a concise onboarding guide. It complements the *Ansible Overview & Usage* and *[Directory Structure & Conventions](ansible_directory_structure_&_conventions.md)* by serving as a one‑page reference for essential commands.

---

## Checking Out the Code from GitHub
Before working with Ansible, clone the repository and keep it up to date:

{% raw %}
```shell
# Clone the repository (first time)
git clone https://github.com/t3knoid/ansible.git
cd ansible

# Update to the latest version (subsequent use)
git pull
```
{% endraw %}

**Notes:**
- Always run `git pull` before executing playbooks to ensure you are working with the latest codebase.  
- For contributions, create a feature branch before making changes:  
  ```shell
  git checkout -b feature/my-change
  ```

---

## Environment Setup
1. **Connect to a control node** (e.g., via SSH).  
2. **Activate Python environment**:  
   ```shell
   source /opt/python_3.12/bin/activate
   ```  
3. **Navigate to the Ansible repository**:  
   ```shell
   cd ~/ansible
   ```  
4. **Update to the latest codebase**:  
   ```shell
   git pull
   ```

---

## Deploy or Update Ansible
Run the following command to deploy or update Ansible:

{% raw %}
```shell
INV=inventory/ansible/inventory.ini
ansible-playbook -k -i $INV playbooks/ansible/deploy_ansible.yml
```
{% endraw %}

---

## Common Playbooks
| Playbook | Purpose |
|----------|---------|
| `provision_vm.yml` | Provision a new virtual machine |
| `deploy_code_server.yml` | Deploy Code Server IDE |

---

## Privileged Execution
- Use the local **ansible** account during VM provisioning.  
- After provisioning, any user in the **ansible** domain group can elevate privileges to run Ansible commands.  

---

## Alternative Execution via Semaphore UI
> 💡 As an alternative to running playbooks from the console, you can use [Semaphore](semaphore.md) UI for a simplified web interface. It provides a dashboard for managing inventories, credentials, and playbook runs.

---

## Quick Reference Diagram
{% raw %}
```
Workflow:
Clone Repo → SSH → Activate Python → Pull Repo → Run Playbook → (Optional) Manage via Semaphore UI
```
{% endraw %}