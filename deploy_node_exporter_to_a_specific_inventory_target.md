---
title: "Deploy Node Exporter to a Specific Inventory Target"
---

# 🏃 Deploy Node Exporter to a Specific Inventory Target

This runbook provides step-by-step instructions to deploy Node Exporter to the hosts defined in a specific inventory target.

---

## 1️⃣ Login to an Ansible Control Node

Start by logging into a control node that has Ansible installed and prepare the environment:

{% raw %}
```shell
cd ~/ansible
source activate
INV=inventory/<target>/inventory.ini
```
{% endraw %}

Example:

{% raw %}
```shell
INV=inventory/plex/inventory.ini
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

## 3️⃣ Confirm the Inventory Target Includes node_exporter Hosts

Open the target inventory and confirm the desired hosts or groups are included in the node_exporter membership.

Examples:

{% raw %}
```ini
[node_exporter]
plex-0
```
{% endraw %}

or

{% raw %}
```ini
[node_exporter:children]
lidarr
sonarr
radarr
```
{% endraw %}

Also ensure the inventory defines the node exporter port in its group vars:

{% raw %}
```yaml
node_exporter_port: 9200
```
{% endraw %}

> ⚡ Important: The inventory is the source of truth for which hosts receive Node Exporter and which hosts Prometheus will scrape.

---

## 4️⃣ Deploy Node Exporter

Run the following command to deploy Node Exporter:

{% raw %}
```shell
ansible-playbook -i $INV -k -u ansible playbooks/prometheus/deploy_node_exporter.yml
```
{% endraw %}

> ⚡ Note: The -k option prompts for SSH password if needed.

This playbook installs or updates Node Exporter on the hosts in the node_exporter group for the selected inventory.

---

## 5️⃣ Refresh Prometheus Exporter Targets

This repo separates the deployment step from the Prometheus target refresh step. After deploying Node Exporter, refresh the scrape targets so Prometheus begins monitoring the hosts from the selected inventory:

{% raw %}
```shell
ansible-playbook -i $INV -k -u ansible deploy_prometheus_exporters.yml
```
{% endraw %}

> ⚡ Important: Deploying Node Exporter alone does not update Prometheus scrape targets.

---

## Verify Deployment

After deployment, verify both the exporter and Prometheus target status.

### Check the exporter endpoint on a target host

{% raw %}
```shell
curl -fsS http://<target-host>:9200/metrics | head
```
{% endraw %}

You should see Prometheus-format metrics output.

### Check the target list in Prometheus

{% raw %}
```shell
curl -fsS 'http://<prometheus-host>:9090/api/v1/targets' | jq '.data.activeTargets[] | select(.labels.job=="node")'
```
{% endraw %}

You should see the selected inventory hosts listed under the node job.

### Check the health query

{% raw %}
```shell
curl -fsS 'http://<prometheus-host>:9090/api/v1/query?query=up{job="node"}' | jq
```
{% endraw %}

Expected result: values should be 1 for healthy hosts.

### Check a standard node exporter metric

{% raw %}
```shell
curl -fsS 'http://<prometheus-host>:9090/api/v1/query?query=node_time_seconds{job="node"}' | jq
```
{% endraw %}

You should see time series returned for the deployed hosts.

---

### ✅ Notes

- Use the nearest existing pattern already present in the inventory for node_exporter membership.
- Common repo convention is node_exporter_port: 9200 at the inventory level.
- Run the Prometheus refresh playbook against the same inventory you used for deployment.
- If you only want a subset of the inventory’s node_exporter hosts, use Ansible limit with the deploy command.

Example:

{% raw %}
```shell
ansible-playbook -i $INV -k -u ansible deploy_node_exporter.yml --limit plex-0
```
{% endraw %}

- You should refresh Prometheus after a limited deploy only if the inventory membership changed or Prometheus config needs to be re-rendered.
```
