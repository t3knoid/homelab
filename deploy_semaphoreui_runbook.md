---
title: "Deploy SemaphoreUI Runbook"
---

# 🏃 Deploy SemaphoreUI Runbook

This runbook provides **step-by-step instructions to deploy or update SemaphoreUI** in the Home Lab using the corresponding Ansible playbook.

---

## 1️⃣ Login to an Ansible Control Node

Start by logging into a control node with Ansible installed and prepare the environment:

{% raw %}
```shell
cd ~/ansible
source /opt/python_3.12/bin/activate
INV=inventory/ansible/inventory.ini
```
{% endraw %}

> ⚡ Important: Always start on the control node so all subsequent commands run in the correct environment.

---

## 2️⃣ Pull the Latest Code

Ensure your local repository is up to date:

{% raw %}
```shell
git pull origin main
```
{% endraw %}

> ⚡ Important: Pulling the latest code first prevents conflicts and ensures you’re working with the most recent version.

---

## 3️⃣ Set Version to Deploy

Edit the file:

{% raw %}
```
inventory/ansible/group_vars/semaphore/main.yml
```
{% endraw %}

Locate the variable:

{% raw %}
```
semaphoreui_setup_version
```
{% endraw %}

and set it to the **desired version** of SemaphoreUI.

Example format:

{% raw %}
```yaml
semaphoreui_setup_version: "2.16.17"
```
{% endraw %}

* Find the list of releases from the official [SemaphoreUI releases page](https://github.com/semaphoreui/semaphore/releases).

---

## 4️⃣ Commit Version Change

After updating the version value, commit your changes to the repository:

{% raw %}
```shell
git add inventory/ansible/group_vars/semaphore/main.yml
git commit -m "Update SemaphoreUI version to <version_number>"
git push origin main
```
{% endraw %}

> ⚡ Important: Replace `<version_number>` with the actual version you set.

---

## 5️⃣ Deploy SemaphoreUI

Run the following command to deploy or update SemaphoreUI:

{% raw %}
```shell
ansible-playbook -i $INV -k playbooks/plex/deploy_semaphoreui.yml
```
{% endraw %}

> ⚡ Note: The `-k` option will prompt for an SSH password if required.

---

## 6️⃣ Verify Deployment

After the playbook runs:

1. Open a web browser and navigate to:
   [https://semaphore.refol.us](https://semaphore.refol.us)
2. Log in as an administrator.
3. Click on the **Admin** link (or similar UI element) to view the installed version.
4. Confirm that the **version number matches** the version you set.

---

### ✅ Notes

* Make sure you choose a valid release version from the official SemaphoreUI releases. ([Home Lab][1])
* Always pull the latest code first to avoid merge conflicts.
* If the deployment fails, check playbook syntax and that the inventory variable `INV` points to the correct hosts.

