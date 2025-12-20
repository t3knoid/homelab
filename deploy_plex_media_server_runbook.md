---
title: "Deploy Plex Media Server Runbook"
---

# 🏃 Deploy Plex Media Server Runbook

This runbook provides **step-by-step instructions to deploy or update Plex Media Server** in the Home Lab. It uses the `deploy_plex.yml` Ansible playbook. Follow the steps carefully to ensure the service is updated correctly and the intended version is installed.

---

## 1️⃣ Login to an Ansible Control Node

Start by logging into a control node with Ansible installed and prepare the environment:

{% raw %}
```shell
cd ~/ansible
source /opt/python_3.12/bin/activate
INV=inventory/plex/inventory.ini
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

## 3️⃣ Set Plex Version

Edit the file:

{% raw %}
```
inventory/plex/group_vars/all/main.yml
```
{% endraw %}

Set the variable:

{% raw %}
```
plex_setup_version
```
{% endraw %}

to the **version you want to deploy**.

Example:

{% raw %}
```yaml
plex_setup_version: "1.41.4.9463-630c9f557"
```
{% endraw %}

* Find the latest version from [Plex Media Server Downloads](https://www.plex.tv/media-server-downloads/?cat=computer&plat=linux#plex-media-server).
* Copy the version string exactly as shown on the page, **without the preceding "v"**.

---

## 4️⃣ Commit Version Change

After updating the version, commit your changes to the repository:

{% raw %}
```shell
git add inventory/plex/group_vars/all/main.yml
git commit -m "Update Plex Media Server version to <version_number>"
git push origin main
```
{% endraw %}

> ⚡ Important: Replace `<version_number>` with the actual version you set.

---

## 5️⃣ Deploy Plex Media Server

Run the following command to deploy or update Plex:

{% raw %}
```shell
ansible-playbook -i $INV -k playbooks/plex/deploy_plex.yml
```
{% endraw %}

> ⚡ Note: The `-k` option prompts for SSH password if needed.

---

## 6️⃣ Verify Installed Version

After deployment:

1. Open [https://www.plex.tv/](https://www.plex.tv/) in your browser.
2. Login using administrator credentials.
3. Click the **Settings** icon (top-right corner).
4. Navigate the left menu and select **General** from the **Settings** sub-menu.
5. Confirm that the **installed version matches the version you set** in the configuration.

---

### ✅ Notes

* Always double-check the version before deploying.
* Use this workflow for both **updates and new deployments**.
* Ensure the control node has network access to Plex.
* Pulling, committing, and deploying in this order keeps your repository consistent and prevents accidental overwrites.

