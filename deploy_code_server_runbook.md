---
title: "🏃 Deploy Code Server Runbook"
---

# 🏃 Deploy Code Server Runbook

This runbook provides **step-by-step instructions to deploy or update Code Server** using Ansible.

---

## 1️⃣ Login to an Ansible Control Node

Start by logging into an Ansible control node and prepare the environment:

```shell
cd ~/ansible
source /opt/python_3.12/bin/activate
INV=inventory/ansible/inventory.ini
```

> ⚡ Important: Always begin on the control node so all commands run in the correct environment.

---

## 2️⃣ Pull the Latest Code

Ensure your local Ansible repository is up to date:

```shell
git pull origin main
```

> ⚡ Important: Pulling the latest code first prevents conflicts and ensures you’re working with the most recent configuration.

---

## 3️⃣ Set Version to Deploy

1. Open the Code Server releases page to identify the latest version:
   [https://github.com/coder/code-server/releases](https://github.com/coder/code-server/releases)

2. Edit the following file:

   ```
   inventory/ansible/group_vars/code_server/main.yml
   ```

3. Update the version variable:

   ```yaml
   code_server_version: 4.100.2
   ```

---

## 4️⃣ Commit Version Change

After updating the version, commit the change:

```shell
git add inventory/ansible/group_vars/code_server/main.yml
git commit -m "Update Code Server version to 4.100.2"
git push origin main
```

> ⚡ Important: Always commit version changes before deployment.

---

## 5️⃣ Deploy the Update

Run the Ansible playbook to deploy the new Code Server version:

```shell
ansible-playbook -i $INV -k playbooks/deploy_code_server.yml
```

> ⚡ Note: The `-k` option will prompt for an SSH password if required.

---

## 6️⃣ Verify Update

Verify the update completed successfully:

1. Open a web browser and navigate to:
   [https://code.refol.us/](https://code.refol.us/)
2. Click the **ellipsis (⋯)** menu.
3. Select **Help → About**.
4. Confirm the displayed version matches the version you deployed.

---

### ✅ Notes

* Always pull and commit version changes before deploying.
* Ensure the inventory variable (`INV`) points to the correct hosts.
* If the deployment fails, review the Ansible output for errors before retrying.

