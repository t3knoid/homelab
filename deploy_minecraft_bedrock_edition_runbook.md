# 🏃 Deploy Minecraft Bedrock Edition Runbook

This runbook provides **step-by-step instructions to deploy or update a Minecraft Bedrock Edition server** using Ansible.

---

## 1️⃣ Login to an Ansible Control Node

Start by logging into an Ansible control node and prepare the environment:

```shell
cd ~/ansible
source /opt/python_3.12/bin/activate
INV=inventory/minecraft/inventory.ini
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
inventory/minecraft/group_vars/all/main.yml
```

Locate and update the version variable:

```yaml
bedrock_setup_version: 1.21.83.1
```

### How to Find the Latest Version

1. Open the Minecraft Bedrock server download page:
   [https://www.minecraft.net/en-us/download/server/bedrock](https://www.minecraft.net/en-us/download/server/bedrock)
2. Hover over the **Download** button to reveal the download URL.

Example URL:

```
https://www.minecraft.net/bedrockdedicatedserver/bin-linux/bedrock-server-1.21.83.1.zip
```

The version number is the **suffix of the filename**:

```
1.21.83.1
```

---

## 4️⃣ Commit Version Change

After updating the version, commit the change:

```shell
git add inventory/minecraft/group_vars/all/main.yml
git commit -m "Update Minecraft Bedrock version to 1.21.83.1"
git push origin main
```

> ⚡ Important: Always commit version changes before deploying.

---

## 5️⃣ Deploy the Update

Run the Ansible playbook to deploy the new Bedrock version:

```shell
ansible-playbook -i $INV -k playbooks/minecraft/deploy_bedrock.yml
```

> ⚡ Note: The `-k` option will prompt for an SSH password if required.

---

## 6️⃣ Verify Installed Version

Connect to the Minecraft Bedrock server host (for example, `minecraft-1`) and inspect the service logs:

```shell
sudo journalctl -u bedrock -xe
```

You should see output similar to the following, confirming the installed version:

```text
May 27 14:47:16 minecraft-1 bedrock_server[29243]: [2025-05-27 14:47:16:835 INFO] Starting Server
May 27 14:47:16 minecraft-1 bedrock_server[29243]: [2025-05-27 14:47:16:835 INFO] Version: 1.21.83.1
```

---

### ✅ Notes

* Always pull and commit version changes before deploying.
* Ensure the Minecraft host is reachable via the inventory defined in `INV`.
* If the service fails to start, review the full journal output for errors.
