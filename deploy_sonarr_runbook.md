# 🏃 Deploy Sonarr Runbook

This runbook provides **step‑by‑step instructions to deploy or update Sonarr** in the Home Lab using a corresponding Ansible playbook.

---

## 1️⃣ Login to an Ansible Control Node

Start by logging into a control node that has Ansible installed and prepare the environment:

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

Edit the following file:

```
inventory/services/group_vars/sonarr/main.yml
```

Locate and update the version variable:

```
sonarr_setup_version: <desired_version>
```

To find the latest stable version:

1. Visit **Sonarr’s GitHub Versions page** and look for the release tagged `latest`.
   (The repository contains all tagged builds — choose the appropriate one for deployment.) ([Home Lab][1])

---

## 4️⃣ Commit Version Change

After updating the version, commit the change:

```shell
git add inventory/services/group_vars/sonarr/main.yml
git commit -m "Update Sonarr version to <version_number>"
git push origin main
```

> ⚡ Important: Replace `<version_number>` with the actual version you’re deploying.

---

## 5️⃣ Deploy Sonarr

Run the Ansible playbook to deploy the new version:

```shell
ansible-playbook -i $INV -k playbooks/services/deploy_sonarr.yml
```

> ⚡ Note: The `-k` option will prompt for an SSH password if required.

---

## 6️⃣ Verify Installed Version

After the playbook completes:

1. Open a web browser and navigate to:
   [https://sonarr.refol.us](https://sonarr.refol.us)
2. In the web interface, go to **System > Status**.
3. Confirm that the **shown version matches the one you just deployed**.

---

### ✅ Notes

* Always pull and commit code before running the playbook.
* Make sure the inventory variable (`INV`) correctly references the target hosts.
* If the deployment fails, check the Ansible output for errors before retrying.

