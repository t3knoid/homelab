---
title: "Enable Code Server runbook"
---

# 🏃 Enable Code Server runbook

This runbook provides **step-by-step instructions to enable and start Code Server** using Ansible.

---

## 1️⃣ Login to an Ansible Control Node

Start by logging into an Ansible control node and prepare the environment:

{% raw %}
```shell
cd ~/ansible
source /opt/python_3.12/bin/activate
INV=inventory/ansible/inventory.ini
```
{% endraw %}

> ⚡ Important: Always begin on the control node so all commands run in the correct environment.

---

## 2️⃣ Pull the Latest Code

Ensure your local Ansible repository is up to date:

{% raw %}
```shell
git pull origin main
```
{% endraw %}

> ⚡ Important: Pulling the latest code first prevents conflicts and ensures you’re working with the most recent configuration.

---

## 3️⃣ Run the Ansible Playbook

Run the Ansible playbook to stop and disable Code Server version:

{% raw %}
```shell
ansible-playbook -i $INV -k playbooks/enable_code_server.yml
```
{% endraw %}

> ⚡ Note: The `-k` option will prompt for an SSH password if required.

---

## 6️⃣ Verify Code Server is Enabled

Verify that Code Server is available.

1. Open a web browser and navigate to:
   [https://code.refol.us/](https://code.refol.us/)
2. The Code Server UI should be what is shown.

---

### ✅ Notes

* Always pull and commit version changes before deploying.
* Ensure the inventory variable (`INV`) points to the correct hosts.
* If the deployment fails, review the Ansible output for errors before retrying.

