---
title: "Update Pi-hole DNS Servers Runbook"
---

# 🏃 Update Pi-hole DNS Servers Runbook

This runbook provides **step-by-step instructions to update Pi-hole DNS Servers** in the Home Lab. It uses the `update_pihole_dns.yml` Ansible playbook. Follow the steps carefully to ensure the update is applied safely and successfully.

---

## 1️⃣ Login to an Ansible Control Node

Start by logging into a control node with Ansible installed and prepare the environment:

{% raw %}
```shell
cd ~/ansible
source /opt/python_3.12/bin/activate
INV=inventory/dns/inventory.ini
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

## 3️⃣ Check for Pi-hole Updates

Open the Pi-hole interface to see if an update is available. Take note of the version to be applied.

> ⚡ Tip: The interface will show a notification when a new version is available.

---

## 4️⃣ Deploy Pi-hole Update

Run the Ansible playbook to update Pi-hole DNS Servers:

{% raw %}
```shell
ansible-playbook -i $INV -k playbooks/dns/update_pihole_dns.yml
```
{% endraw %}

> ⚡ Note: The `-k` option prompts for SSH password if needed.

---

## 5️⃣ Verify Installed Version

After deployment:

1. Open [http://dns-1.refol.us/admin/](http://dns-1.refol.us/admin/) in your browser.
2. Login using administrator credentials.
3. Confirm that the **version information at the bottom of the screen matches the expected update**.

---

### ✅ Notes

* Always take a VM snapshot before updating to allow rollback.
* Use this workflow for both updates and new deployments.
* Pulling the latest code first ensures your repository is up to date.
* Make sure the control node has network access to Pi-hole.

