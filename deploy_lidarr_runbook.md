---
title: "Deploy Lidarr Runbook"
---

# 🏃 Deploy Lidarr Runbook

This runbook provides **step-by-step instructions to deploy or update Lidarr** in the Home Lab. It uses the `deploy_lidarr.yml` Ansible playbook. Follow the steps carefully to ensure the service is deployed correctly and the latest version is installed.

---

## 1️⃣ Login to an Ansible Control Node

Start by logging into a control node that has Ansible installed and prepare the environment:

{% raw %}
```shell
cd ~/ansible
source /opt/python_3.12/bin/activate
INV=inventory/services/inventory.ini
```
{% endraw %}

> ⚡ Important: Always start on the control node so all subsequent commands run in the correct environment.

---

## 2️⃣ Pull the Latest Code

Before making any changes, ensure your local repository is up to date:

{% raw %}
```shell
git pull origin main   # Pull the latest code
```
{% endraw %}

> ⚡ Important: Pulling the latest code first prevents conflicts and ensures you’re working on the most recent version.

---

## 3️⃣ Set Version to Deploy

Edit the file:

{% raw %}
```
inventory/services/group_vars/lidarr/main.yml
```
{% endraw %}

Set the variable:

{% raw %}
```
lidarr_setup_version
```
{% endraw %}

to the **version you want to deploy**.

* Find the latest stable version from [Lidarr's GitHub Versions page](https://github.com/linuxserver/docker-lidarr/pkgs/container/lidarr/versions?filters%5Bversion_type%5D=tagged).
* Look for the **'latest' build tag**.

> ⚡ Tip: This same process is used when updating Lidarr to a new version.

---

## 4️⃣ Commit Version Change

After updating the version, commit your changes to the repository:

{% raw %}
```shell
git add inventory/services/group_vars/lidarr/main.yml
git commit -m "Update Lidarr version to <version_number>"
git push origin main   # Push your changes to GitHub
```
{% endraw %}

> ⚡ Important: Replace `<version_number>` with the actual version you set.

---

## 5️⃣ Deploy Lidarr

Run the following command to deploy Lidarr:

{% raw %}
```shell
ansible-playbook -i $INV -k playbooks/services/deploy_lidarr.yml
```
{% endraw %}

> ⚡ Note: The `-k` option prompts for SSH password if needed.

---

## 6️⃣ Verify Installed Version

After deployment:

1. Open [https://lidarr.refol.us](https://lidarr.refol.us) in your browser.
2. Navigate to **System > Status**.
3. Confirm the **version number matches the version you set** in the configuration.

---

### ✅ Notes

* Always double-check the version before deploying.
* Always take a VM snapshot before updating to allow rollback.
* Use this same workflow for **updates**, not just new deployments.
* Ensure the control node has network access to your Home Lab services.
* Starting on the control node, pulling the latest code, and committing changes first keeps your repository consistent and prevents accidental overwrites.

