---
title: "Deploy Grafana Dashboards"
---

# 📊 Deploy Grafana Dashboards

Use [deploy_grafana_dashboards.yml](https://github.com/t3knoid/ansible/tree/main/playbooks/grafana/deploy_grafana_dashboards.yml) to update provisioned dashboard files on an existing Grafana installation. This path does not install Grafana or Azure CLI, register/rotate Entra credentials, change Grafana authentication, update data sources, or manage the PostgreSQL database.

## 📋 Prerequisites

- Run from the repository root using the normal Ansible environment and Grafana inventory credentials.
- Grafana must already be installed/configured with its service account, service, and provisioning path. The task checks for the existing `grafana_setup_config_file` before making dashboard changes.
- The dashboards' referenced data sources must already exist. In particular, the PostgreSQL Status dashboard references the Prometheus data source with UID `prometheus`.
- Confirm the inventory's dashboard/provider paths refer to the running installation. This path does not rewrite Grafana's main configuration to point at new provisioning directories.

## 🔎 Preview

{% raw %}
```bash
ansible-playbook -i inventory/grafana/inventory.ini playbooks/grafana/deploy_grafana_dashboards.yml --syntax-check
ansible-playbook -i inventory/grafana/inventory.ini playbooks/grafana/deploy_grafana_dashboards.yml --list-tasks
ansible-playbook -i inventory/grafana/inventory.ini playbooks/grafana/deploy_grafana_dashboards.yml --check --diff
```
{% endraw %}

Add the usual vault password/identity, SSH, or become options if required. Use `--limit grafana-0` to select that existing host when appropriate. The path updates the complete repository-managed dashboard set, not only the PostgreSQL dashboard.

## ▶️ Deploy

{% raw %}
```bash
ansible-playbook -i inventory/grafana/inventory.ini playbooks/grafana/deploy_grafana_dashboards.yml
```
{% endraw %}

The shared [dashboard tasks](https://github.com/t3knoid/ansible/tree/main/roles/grafana_setup/tasks/dashboards.yml) create the dashboard provisioning directories, render the file provider, and install the same dashboard set used by the full Grafana deployment. They also remove the explicitly retired `proxmox-vm-snapshots.dashboard.json` file, matching the existing full-deployment cleanup; unrelated dashboard files are not pruned.

Dashboard JSON changes are picked up by Grafana's file provider without a service restart. The configured `grafana_setup_dashboard_update_interval_seconds` defaults to 30 seconds. If the provider definition itself changes, the existing `Restart Grafana` handler runs at the end of the play so Grafana loads the new provider settings; plan for a brief interruption in that case.

## ✅ Verify and Troubleshoot

- Open the configured dashboard folder (default `Infrastructure`) and refresh the relevant dashboard after the provider interval.
- For PostgreSQL Status, check the PostgreSQL Host Memory Usage graph. It reports database host memory, not PostgreSQL-only process memory; it requires Node Exporter metrics with instance labels matching the PostgreSQL Exporter targets.
- If a dashboard is missing, verify its destination file, provider path, permissions, and Grafana provisioning logs. If a panel shows No Data, inspect the data source and Prometheus query rather than reinstalling Grafana or rerunning Entra registration.
- If the existing-configuration assertion fails, inspect the configured path or perform the separately reviewed [full Grafana deployment](https://github.com/t3knoid/ansible/tree/main/playbooks/grafana/deploy_grafana.yml). Do not bypass the prerequisite merely to create dashboard files on an unconfigured host.
- Roll back dashboard changes through the repository and rerun this dashboard-only path. File-provisioned dashboards may overwrite UI edits according to the provider policy; keep intentional changes in their source JSON files.
