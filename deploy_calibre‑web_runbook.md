---
title: "🏃 Deploy Calibre‑web Runbook"
---

# 🏃 Deploy Calibre‑web Runbook

This runbook provides **step‑by‑step instructions to deploy or update Calibre‑web** in the Home Lab using Ansible.

---

## 1️⃣ Login to an Ansible Control Node

Start by logging into an Ansible control node and prepare the environment:

```shell
cd ~/ansible
source /opt/python_3.12/bin/activate
INV=inventory/services/inventory.ini
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

Edit the file:

```
inventory/services/group_vars/calibre/main.yml
```

Locate and update the version variable:

```yaml
calibreweb_setup_version: <desired_version>
```

### Where to Find the Latest Version

* Visit **Calibre‑web’s GitHub Versions page** and look for the release tagged `latest`.
  Use that version for deployment. ([Home Lab][1])

---

## 4️⃣ Commit Version Change

After updating the version value, commit the change:

```shell
git add inventory/services/group_vars/calibre/main.yml
git commit -m "Update Calibre‑web version to <version_number>"
git push origin main
```

> ⚡ Important: Replace `<version_number>` with the actual version you are deploying.

---

## 5️⃣ Deploy Calibre‑web

Run the Ansible playbook to deploy the specified version:

```shell
ansible-playbook -i $INV -k playbooks/services/deploy_calibreweb.yml
```

> ⚡ Note: The `‑k` option will prompt for an SSH password if required.

---

## 6️⃣ Verify Installed Version

After deployment:

1. Open a web browser and navigate to:
   [https://books.refol.us](https://books.refol.us)
2. Click **About** (from the menu).
3. Confirm that the **version number shown matches** the version you set. ([Home Lab][1])

---

### ✅ Notes

* Always pull and commit changes before deploying.
* Make sure the inventory variable (`INV`) points to the correct hosts.
* If deployment fails, review the Ansible output for errors before retrying.

