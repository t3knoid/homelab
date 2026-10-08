---
title: "Ubuntu 26.04 LTS Release Upgrade Runbook"
---

# 🏃 Ubuntu 26.04 LTS Release Upgrade Runbook

This runbook provides **step-by-step instructions to upgrade one Ubuntu 24.04 LTS VM to Ubuntu 26.04 LTS** using the existing Ansible VM role and release-upgrade playbook.

---

## 1️⃣ Login to an Ansible Control Node

Start on a control node with Ansible and the repository environment available:

{% raw %}
```shell
cd ~/ansible
source /opt/python_3.12/bin/activate
INV=inventory/services/inventory.ini
```
{% endraw %}

> ⚡ Important: Run the playbook from the Ansible control node, not from the VM being upgraded.

---

## 2️⃣ Pull the Latest Code

Check for local changes, then update the repository:

{% raw %}
```shell
git status --short
git pull --ff-only origin main
```
{% endraw %}

If you have uncommitted changes, resolve or preserve them before pulling.

---

## 3️⃣ Select and Verify the VM

Set the inventory hostname. `lidarr-0` is an example; replace it with the single VM you intend to upgrade:

{% raw %}
```shell
HOST=lidarr-0
ansible vms -i "$INV" --list-hosts --limit "$HOST"
ansible "$HOST" -i "$INV" -m ansible.builtin.setup -a 'filter=ansible_distribution*'
```
{% endraw %}

Proceed only if the host list contains exactly one VM and its facts report Ubuntu 24.04. The playbook rejects other source releases and upgrades only to 26.04.

---

## 4️⃣ Confirm the Rollback Plan

Schedule a maintenance window and confirm you have a usable backup. The playbook creates a uniquely named Proxmox snapshot before package changes, using the existing `vms` role. Confirm Proxmox snapshot storage has sufficient space and the control node can access the configured Proxmox API.

The snapshot does not include VM memory state. Keep it until the application and host have been verified; follow your normal retention process before removing it.

---

## 5️⃣ Run the Release Upgrade

Run the dedicated playbook, explicitly limiting it to the selected VM and confirming the release upgrade:

{% raw %}
```shell
ansible-playbook -i "$INV" playbooks/vms/release_upgrade_ubuntu.yml \
  --limit "$HOST" \
  -e vms_ubuntu_release_upgrade_confirm=true
```
{% endraw %}

The playbook updates installed packages first, installs/configures Ubuntu's release upgrader for LTS releases, runs `do-release-upgrade`, reconnects, and verifies Ubuntu reports version 26.04. It also performs a reboot when required. Use `-k` if Ansible needs an SSH password or `-K` if it needs a become password.

> ⚡ Important: Do not omit `--limit` or the explicit confirmation. The playbook is intentionally guarded to run against exactly one host.

---

## 6️⃣ Verify the Upgrade

Wait for the playbook to finish successfully, then confirm the reported OS version:

{% raw %}
```shell
ansible "$HOST" -i "$INV" -m ansible.builtin.setup -a 'filter=ansible_distribution_version'
```
{% endraw %}

Confirm the facts report `26.04`, then check the service is healthy. For the Lidarr example, open `https://lidarr.refol.us` and verify the application loads and is operational.

If the playbook fails after the release-upgrade command starts, inspect the VM's current state and Ansible output before retrying. Do not rerun blindly; use the Proxmox snapshot only through your normal recovery procedure.

---

### ✅ Notes

- This workflow supports Ubuntu 24.04 LTS to Ubuntu 26.04 LTS only.
- No inventory version change is needed; the target release is fixed in the playbook.
- Use this playbook for one VM per run, then verify it before upgrading another VM.
- Do not add `-d`; the playbook is for the stable LTS release path.
- Keep a separate backup; a VM snapshot is not a substitute for your backup policy.
