---
title: "Configure Grafana Dashboards Process"
---

# Configure Grafana Dashboards Process

## Purpose

This runbook defines the dashboard-as-code workflow for Grafana in this repository.

## Principles

1. Store dashboard JSON files in the repository.
2. Provision datasources and dashboards through Ansible.
3. Avoid manual dashboard edits in Grafana UI for persistent changes.
4. Keep upstream dashboard sources and local adaptations in source control.

## Role Components

- Dashboard and datasource defaults: roles/grafana_setup/defaults/main/main.yml
- Provisioning tasks: roles/grafana_setup/tasks/main.yml
- Datasource provisioning template: roles/grafana_setup/templates/provisioning-datasources.yml.j2
- Dashboard provider provisioning template: roles/grafana_setup/templates/provisioning-dashboards.yml.j2
- Vendored dashboard files: roles/grafana_setup/files/dashboards/nginx-prometheus-exporter.dashboard.json
- Deployment playbook: playbooks/grafana/deploy_grafana.yml
- Grafana inventory: inventory/grafana/inventory.ini

## Standard Workflow

1. Choose an upstream dashboard JSON or create a custom one.
2. Save dashboard JSON under roles/grafana_setup/files/dashboards.
3. Ensure datasource and provider provisioning templates are aligned.
4. Deploy Grafana using playbooks/grafana/deploy_grafana.yml.
5. Validate dashboard panels and datasource connectivity in Grafana UI.

## Provisioning Flow

1. Grafana role creates provisioning directories.
2. Grafana role renders datasource provisioning file.
3. Grafana role renders dashboard provider provisioning file.
4. Grafana role copies dashboard JSON files into Grafana dashboards path.
5. Grafana service reload/start applies provisioning.

## Add a New Dashboard

1. Add JSON file to roles/grafana_setup/files/dashboards.
2. If needed, add role defaults in roles/grafana_setup/defaults/main/main.yml.
3. Ensure copy/provisioning tasks in roles/grafana_setup/tasks/main.yml include the dashboard.
4. Run deployment playbook for Grafana hosts.

## Validation Checklist

1. ansible-playbook --syntax-check passes for playbooks/grafana/deploy_grafana.yml.
2. ansible-inventory --graph passes for inventory/grafana/inventory.ini.
3. Grafana service is active after deploy.
4. Prometheus datasource exists and is default.
5. Dashboard appears in expected folder.
6. Panels return data without datasource errors.

## Maintenance

1. Keep dashboard UID stable to avoid duplicate dashboards.
2. Keep local modifications minimal and explicit.
3. Revalidate dashboards when Prometheus metric names or jobs change.
4. Use pull requests for all dashboard changes.
