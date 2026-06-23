---
title: "NGINX Exporter Deployment Runbook"
---

# NGINX Exporter Deployment Runbook

This runbook covers deploying `nginx_prometheus_exporter_setup` and wiring the targets into Prometheus.

## What It Does

NGINX Prometheus Exporter exposes NGINX stub status metrics on port `9113`. In this repository, Prometheus discovers exporter hosts from the `nginx_exporter` inventory group.

## Inventory Requirements

The inventory used for Prometheus deployment should define:

- a `[prometheus]` group for the Prometheus host
- a `[nginx_exporter:children]` group that points at the host groups where the exporter runs

Example pattern:

{% raw %}
```ini
[nginx_exporter:children]
rproxy_main
rproxy_primary
rproxy_secondary
```
{% endraw %}

## Deployment Steps

1. Add the target hosts to the inventory that runs the NGINX exporter.
2. Make sure those hosts are members of the `nginx_exporter` group.
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

1. Confirm the `nginx-prometheus-exporter` service is running on the host.
2. Verify the metrics endpoint locally.
3. Check Prometheus targets for the host.

Useful check:

{% raw %}
```bash
curl http://localhost:9113/metrics
```
{% endraw %}

## Troubleshooting

- If Prometheus does not show the host, confirm it is in the `nginx_exporter` group for the inventory you passed to `deploy_prometheus_exporters.yml`.
- If the exporter is running locally but not visible from Prometheus, verify the host IP in `global_ip_addresses` and any firewall or allow-list rules.
- If the service is missing, re-run the exporter playbook and inspect the systemd unit on the host.