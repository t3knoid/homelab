---
title: "🏃 [Service Name] Runbook"
---

# 🏃 [Service Name] Runbook

This runbook provides **step-by-step instructions to deploy or update [Service Name]** in your Home Lab. It references the corresponding Ansible playbook and ensures consistency, verification, and version control.

---

## 1️⃣ Login to an Ansible Control Node

Start by logging into a control node with Ansible installed and prepare the environment:

```shell
cd ~/ansible
source /opt/python_3.12/bin/activate
INV=inventory/services/inventory.ini
```

> ⚡ Important: Always start on the control node so all subsequent commands run in the correct environment.

---

## 2️⃣ Pull the Latest Code

Ensure your local repository is up to date:

```shell
git pull origin main
```

> ⚡ Important: Pulling the latest code first prevents conflicts and ensures you’re working with the most recent version.

---

## 3️⃣ Set Version or Configuration

Edit the relevant file:

```
[inventory path or config file]
```

Set the variable:

```
[variable_name]
```

to the **desired value/version**.

* Find the latest stable version or configuration from [relevant link].
* Note: Use the same process for updates as for new deployments.

---

## 4️⃣ Commit Configuration Changes

After modifying the configuration, commit your changes:

```shell
git add [file_path]
git commit -m "Update [Service Name] version/config to <value>"
git push origin main
```

> ⚡ Important: Replace `<value>` with the actual version or configuration value.

---

## 5️⃣ Deploy Using Ansible Playbook

Run the corresponding playbook:

```shell
ansible-playbook -i $INV [playbook_file].yml
```

> ⚡ Note: Use `-k` if prompted for SSH password.

---

## 6️⃣ Verify Deployment

After deployment:

1. Open [Service URL or access point].
2. Navigate to **[location in UI or logs]**.
3. Confirm the **version/configuration matches what you set**.

---

### ✅ Notes

* Always double-check the version or configuration before deploying.
* Use this workflow for both **updates and new deployments**.
* Make sure the control node has network access to the service.
* Pulling, committing, and deploying in this order prevents repository conflicts and ensures a consistent deployment state.

