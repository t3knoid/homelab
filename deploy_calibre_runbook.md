---
title: "Deploy Calibre Runbook"
---

# 🏃 Deploy Calibre Runbook

This runbook provides step-by-step instructions to deploy or update Calibre in the Home Lab using Ansible.

---

## 1. Log in to an Ansible Control Node

Prepare the Ansible environment:

{% raw %}
```shell
cd ~/ansible
source /opt/python_3.12/bin/activate
INV=inventory/services/inventory.ini
```
{% endraw %}

Run the deployment from an Ansible control node so it uses the repository's configured environment and inventory.

---

## 2. Pull the Latest Code

{% raw %}
```shell
git pull origin main
```
{% endraw %}

---

## 3. Set the Calibre Version

Edit:

{% raw %}
```text
inventory/services/group_vars/books/main.yml
```
{% endraw %}

Update `calibre_setup_version` to the desired version:

{% raw %}
```yaml
calibre_setup_version: <desired_version>
```
{% endraw %}

Check the available tags for the [LinuxServer Calibre image](https://hub.docker.com/r/linuxserver/calibre/tags) and use a version tag supported by the image. The deployment template uses this value as the container image tag.

---

## 4. Review and Commit the Version Change

Review the diff to ensure only the intended version changed, then commit and push it:

{% raw %}
```shell
git diff -- inventory/services/group_vars/books/main.yml
git add inventory/services/group_vars/books/main.yml
git commit -m "Update Calibre version to <version_number>"
git push origin main
```
{% endraw %}

Replace `<version_number>` with the version being deployed.

---

## 5. Deploy Calibre

{% raw %}
```shell
ansible-playbook -i "$INV" -k playbooks/services/deploy_calibre.yml
```
{% endraw %}

The `-k` option prompts for an SSH password if required.

---

## 6. Verify the Deployment

Open [https://catalog.refol.us](https://catalog.refol.us) and confirm that the Calibre content server responds and displays the library. This hostname serves Calibre; [https://books.refol.us](https://books.refol.us) is the separate Calibre-Web service.

To verify the deployed image tag on `books-0`, run:

{% raw %}
```shell
docker inspect --format='{{.Config.Image}}' calibre
```
{% endraw %}

Confirm the output contains the version set in `calibre_setup_version`.

---

## Notes

- The version variable is in `inventory/services/group_vars/books/main.yml`; it is not `calibreweb_setup_version`.
- The Calibre deployment playbook is `playbooks/services/deploy_calibre.yml`.
- The Ansible inventory group is `calibre`, with host `books-0`.
- Calibre's web content server is exposed at `catalog.refol.us` on port `8081` through the reverse proxy.