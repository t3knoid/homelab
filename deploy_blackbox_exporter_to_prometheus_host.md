---
title: "Deploy Blackbox Exporter to Prometheus host"
---

# 🏃 Deploy Blackbox Exporter to Prometheus host

This runbook provides step-by-step instructions to deploy the Blackbox Exporter for web service probing on the Prometheus hosts.

---

## 1️⃣ Login to an Ansible Control Node

Start by logging into a control node that has Ansible installed and prepare the environment:

{% raw %}
```shell
cd ~/ansible
source activate
INV=inventory/prometheus/inventory.ini
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

## 3️⃣ Deploy Blackbox Exporter

Run the following command to deploy Blackbox Exporter:

{% raw %}
```shell
ansible-playbook -i $INV -k playbooks/prometheus/deploy_blackbox_exporter.yml
```
{% endraw %}

> ⚡ Note: The `-k` option prompts for SSH password if needed.

This playbook installs the Blackbox Exporter service on the hosts in the `blackbox_exporter` group defined by the current inventory. The repo pattern is visible in [inventory/prometheus/inventory.ini](inventory/prometheus/inventory.ini) and the playbook is defined in [playbooks/prometheus/deploy_blackbox_exporter.yml](playbooks/prometheus/deploy_blackbox_exporter.yml).

---

## 4️⃣ Refresh Prometheus Exporter Targets

This repo separates the deployment step from the Prometheus target refresh step. After deploying Blackbox Exporter, refresh the scrape targets so Prometheus begins probing the configured web services:

{% raw %}
```shell
ansible-playbook -i $INV -k playbooks/prometheus/deploy_prometheus_exporters.yml
```
{% endraw %}

> ⚡ Important: The exporter deployment installs the service, but the Prometheus refresh step updates the scrape config from the current inventory.

---

## Verify Deployment

After deployment, verify both the exporter service and the Prometheus target status.

### Check the exporter endpoint on the Prometheus host

{% raw %}
```shell
curl -fsS http://<prometheus-host>:9115/metrics | head
```
{% endraw %}

You should see Prometheus-format metrics output.

### Check the target list in Prometheus

{% raw %}
```shell
curl -fsS 'http://<prometheus-host>:9090/api/v1/targets' | jq '.data.activeTargets[] | select(.labels.job=="blackbox_http")'
```
{% endraw %}

You should see the configured web service targets listed under the `blackbox_http` job.

### Check the health query

{% raw %}
```shell
curl -fsS 'http://<prometheus-host>:9090/api/v1/query?query=probe_success{job="blackbox_http"}' | jq
```
{% endraw %}

Expected result: values should be `1` for healthy services and `0` for failing services.

---

### ✅ Notes

- Blackbox targets are defined in the inventory and are the source of truth for probe targets.
- The exporter service and target list are separate concerns in this repo.
- Deploying the exporter alone does not automatically create the `blackbox_http` job in Prometheus.
- The inventory file is [inventory/prometheus/inventory.ini](inventory/prometheus/inventory.ini).
- The deployment playbook is [playbooks/prometheus/deploy_blackbox_exporter.yml](playbooks/prometheus/deploy_blackbox_exporter.yml).
- The target refresh playbook is [playbooks/prometheus/deploy_prometheus_exporters.yml](playbooks/prometheus/deploy_prometheus_exporters.yml).
- Target definitions live in [inventory/prometheus/group_vars/all/main.yml](inventory/prometheus/group_vars/all/main.yml) under `prometheus