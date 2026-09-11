---
title: "Deploy nginx-prometheus-exporter to Reverse Proxy hosts"
---

# 🏃 Deploy nginx-prometheus-exporter to Reverse Proxy hosts

This runbook provides **step-by-step instructions to deploy the nginx-prometheus-exporter to the Reverse Proxy hosts.

---

## 1️⃣ Login to an Ansible Control Node

Start by logging into a control node that has Ansible installed and prepare the environment:

{% raw %}
```shell
cd ~/ansible
source activate
INV=inventory/rproxy/inventory.ini
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

## 3️⃣ Deploy nginx-prometheus-exporter

Run the following command to deploy nginx-prometheus-exporter:

{% raw %}
```shell
ansible-playbook -i $INV -k -u ansible playbooks/prometheus/deploy_nginx_prometheus_exporter.yml
```
{% endraw %}

> ⚡ Note: The `-k` option prompts for SSH password if needed.

---

## 4️⃣ Refresh Prometheus Exporter Targets

This repo separates the deployment step from the Prometheus target refresh step. After deploying nginx-prometheus-exporter, refresh the scrape targets so Prometheus begins monitoring the new hosts:

{% raw %}
```shell
ansible-playbook -i $INV -k -u ansible playbooks/prometheus/deploy_prometheus_exporters.yml
```
{% endraw %}

> ⚡ Important: The exporter deployment installs the service, but the Prometheus refresh step updates the scrape config from the current inventory.

---

## Verify Deployment

After deployment, verify both the exporter and Prometheus target status.

### Check the exporter endpoint on a Reverse Proxy host

{% raw %}
```shell
curl -fsS http://<rproxy-host>:9113/metrics | head
```
{% endraw %}

You should see Prometheus-format metrics output.

### Check the target list in Prometheus

{% raw %}
```shell
curl -fsS 'http://<prometheus-host>:9090/api/v1/targets' | jq '.data.activeTargets[] | select(.labels.job=="nginx_exporter")'
```
{% endraw %}

You should see the Reverse Proxy hosts listed under the `nginx_exporter` job.

### Check the health query

{% raw %}
```shell
curl -fsS 'http://<prometheus-host>:9090/api/v1/query?query=up{job="nginx_exporter"}' | jq
```
{% endraw %}

Expected result: values should be `1` for healthy hosts.

---

### ✅ Notes

- The inventory is the source of truth for which hosts are scraped by Prometheus.
- Hosts must be members of the `nginx_exporter` group in the inventory for Prometheus to target them.
- Prometheus must be refreshed after adding or updating exporter hosts.
- The deployment playbook is located at deploy_nginx_prometheus_exporter.yml.
- The target refresh playbook is located at deploy_prometheus_exporters.yml.

