---
title: "Deploy PostgreSQL Exporter to the PostgreSQL Inventory"
---

# 🏃 Deploy PostgreSQL Exporter to the PostgreSQL Inventory

This runbook provides step-by-step instructions to deploy Prometheus PostgreSQL Exporter to the hosts defined in the `pg` inventory target.

---

## 1️⃣ Login to an Ansible Control Node

Start by logging into a control node that has Ansible installed and prepare the environment:

{% raw %}
```shell
cd ~/ansible
source activate
INV=inventory/pg/inventory.ini
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

## 3️⃣ Confirm the Inventory Target Includes postgres_exporter Hosts

Open `inventory/pg/inventory.ini` and confirm the desired PostgreSQL hosts are included in the `postgres_exporter` group:

{% raw %}
```ini
[postgres_exporter]
pg-0
pg-1
pg-2
pg-3
pg-4
```
{% endraw %}

Also ensure `inventory/pg/group_vars/all/main.yml` defines the exporter port and database connection settings:

{% raw %}
```yaml
postgres_exporter_port: 9187
postgres_exporter_setup_db_username: "postgres_exporter"
postgres_exporter_setup_db_name: "postgres"
postgres_exporter_setup_db_host: "127.0.0.1"
postgres_exporter_setup_db_port: 5432
postgres_exporter_setup_sslmode: "disable"
```
{% endraw %}

Set `postgres_exporter_setup_db_password` in the inventory vault before deployment.

> ⚡ Important: The inventory is the source of truth for which hosts receive PostgreSQL Exporter and which hosts Prometheus will scrape.

---

## 4️⃣ Deploy PostgreSQL Exporter

Run the following command to deploy PostgreSQL Exporter:

{% raw %}
```shell
ansible-playbook -i $INV -k playbooks/prometheus/deploy_postgres_exporter.yml
```
{% endraw %}

> ⚡ Note: The `-k` option prompts for an SSH password if needed.

This playbook installs or updates PostgreSQL Exporter on the hosts in the `postgres_exporter` group for the selected inventory.

---

## 5️⃣ Refresh Prometheus Exporter Targets

This repo separates the deployment step from the Prometheus target refresh step. After deploying PostgreSQL Exporter, refresh the scrape targets so Prometheus begins monitoring the hosts from the selected inventory:

{% raw %}
```shell
ansible-playbook -i $INV -k playbooks/prometheus/deploy_prometheus_exporters.yml
```
{% endraw %}

> ⚡ Important: Deploying PostgreSQL Exporter alone does not update Prometheus scrape targets.

---

## Verify Deployment

After deployment, verify both the exporter and Prometheus target status.

### Check the exporter endpoint on a target host

{% raw %}
```shell
curl -fsS http://<target-host>:9187/metrics | head
```
{% endraw %}

You should see PostgreSQL Prometheus-format metrics output.

### Check the target list in Prometheus

{% raw %}
```shell
curl -fsS 'http://<prometheus-host>:9090/api/v1/targets' | jq '.data.activeTargets[] | select(.labels.job=="postgres_exporter")'
```
{% endraw %}

You should see the selected PostgreSQL hosts listed under the `postgres_exporter` job.

### Check the health query

{% raw %}
```shell
curl -fsS 'http://<prometheus-host>:9090/api/v1/query?query=up%7Bjob%3D%22postgres_exporter%22%7D' | jq
```
{% endraw %}

Expected result: values should be `1` for healthy exporters.

### Check PostgreSQL exporter health

{% raw %}
```shell
curl -fsS 'http://<prometheus-host>:9090/api/v1/query?query=pg_up%7Bjob%3D%22postgres_exporter%22%7D' | jq
```
{% endraw %}

Expected result: `pg_up` should be `1` when the exporter can connect to PostgreSQL.

---

### ✅ Notes

- Use the existing `postgres_exporter` membership pattern in the inventory.
- The repo convention is `postgres_exporter_port: 9187` at the inventory level.
- Set the exporter database password in the inventory vault before deployment.
- Run the Prometheus refresh playbook against the same inventory used for deployment.
- If you only want a subset of the inventory’s PostgreSQL hosts, use Ansible limit:

{% raw %}
```shell
ansible-playbook -i $INV -k -u ansible playbooks/prometheus/deploy_postgres_exporter.yml --limit pg-0
```
{% endraw %}
