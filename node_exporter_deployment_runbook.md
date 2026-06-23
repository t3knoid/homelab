---
title: "Node Exporter Deployment Runbook"
---

# Node Exporter Deployment Runbook

This runbook covers deploying `node_exporter_setup` and wiring the targets into Prometheus.

## What It Does

Node Exporter exposes Linux host metrics on port `9100`. In this repository, Prometheus discovers Node Exporter hosts from the `node_exporter` inventory group.

## Inventory Requirements

The inventory used for Prometheus deployment should define:

- a `[prometheus]` group for the Prometheus host
- a `[node_exporter:children]` group that points at the host groups where Node Exporter runs

Example pattern:

{% raw %}
```ini
[node_exporter:children]
rproxy_main
rproxy_primary
rproxy_secondary
```
{% endraw %}

## Deployment Steps

1. Add the target hosts to the inventory that runs Node Exporter.
2. Make sure those hosts are members of the `node_exporter` group.
3. Deploy the exporter role.
4. Redeploy Prometheus so the scrape config is rebuilt.

Example:

{% raw %}
```bash
ansible-playbook -k -i inventory/rproxy/inventory.ini playbooks/rproxy/deploy_rproxy.yml
ansible-playbook -k -i inventory/rproxy/inventory.ini playbooks/prometheus/deploy_prometheus_exporters.yml
```
{% endraw %}

## Validation

After the playbooks finish:

1. Confirm the `node_exporter` service is running on the host.
2. Verify the metrics endpoint locally.
3. Check Prometheus targets for the host.

Useful check:

{% raw %}
```bash
curl http://localhost:9100/metrics
```
{% endraw %}

## Troubleshooting

- If Prometheus does not show the host, confirm it is in the `node_exporter` group for the inventory you passed to `deploy_prometheus.yml`.
- If the exporter is running locally but not visible from Prometheus, verify the host IP in `global_ip_addresses` and any firewall rules.
- If the service is missing, re-run the exporter playbook and inspect the systemd unit on the host.