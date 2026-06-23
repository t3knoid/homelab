---
title: "Add a New Grafana Dashboard Runbook"
---

# Add a New Grafana Dashboard Runbook

## Purpose

This runbook describes the process for adding a new Grafana dashboard in this repository using the existing dashboard-as-code pattern.

## Scope

- Grafana dashboard JSON files managed by Ansible
- Grafana datasource/dashboard provisioning managed by the `grafana_setup` role

## Steps

### 1. Add JSON file to role dashboards folder
Add the dashboard JSON file to:

- `roles/grafana_setup/files/dashboards`

Example:

{% raw %}
```bash
cp /path/to/your-dashboard.json roles/grafana_setup/files/dashboards/my-dashboard.json
```
{% endraw %}

Notes:
- Prefer upstream dashboard JSON as a base when available.
- Keep dashboard UID stable to avoid duplicate dashboards in Grafana.

### 2. Add role defaults when needed

If the dashboard needs new settings, add defaults in:

- `roles/grafana_setup/defaults/main/main.yml`

Typical examples:
- Datasource name/UID
- Folder name
- Dashboard provider update interval

Only add variables that are required for this dashboard.

### 3. Ensure copy/provisioning tasks include the dashboard

Confirm provisioning and copy logic in:

- `roles/grafana_setup/tasks/main.yml`

Confirm these are present and aligned:

- Datasource provisioning template task
- Dashboard provider provisioning template task
- Copy task for the dashboard JSON into Grafana dashboards path

Also confirm templates are correct:

- `roles/grafana_setup/templates/provisioning-datasources.yml.j2`
- `roles/grafana_setup/templates/provisioning-dashboards.yml.j2`

### 4. Run deployment playbook for Grafana hosts

Deploy changes with the Grafana playbook:

{% raw %}
```bash
ansible-playbook -i inventory/grafana/inventory.ini playbooks/grafana/deploy_grafana.yml
```
{% endraw %}

## Validation

Run these checks before or after deployment:

{% raw %}
```bash
ansible-playbook --syntax-check -i inventory/grafana/inventory.ini playbooks/grafana/deploy_grafana.yml
ansible-inventory -i inventory/grafana/inventory.ini --graph
```
{% endraw %}

After deployment, validate in Grafana UI:
- Dashboard appears in the configured folder
- Panels load data
- Prometheus datasource resolves successfully

## Troubleshooting

- Dashboard not visible:
  - Confirm JSON exists under `roles/grafana_setup/files/dashboards`
  - Confirm copy task in `roles/grafana_setup/tasks/main.yml` points to the same filename
  - Check Grafana service logs

- Panels show datasource errors:
  - Verify datasource provisioning template values
  - Verify Prometheus host URL resolution from inventory/group vars

- Dashboard duplicates:
  - Ensure dashboard UID remains stable across updates
