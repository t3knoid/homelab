---
title: "Grafana Ansible Role"
---

# Grafana Ansible Role

## Overview

The `grafana_setup` role installs and configures Grafana on Debian/Ubuntu hosts, provisions Prometheus as the default datasource, deploys a file-based dashboard set, configures LDAP authentication, and connects Grafana to a PostgreSQL backend.

The primary deployment playbook is `playbooks/grafana/deploy_grafana.yml`, which applies:

- `global`
- `grafana_setup`

The role expects supporting infrastructure to exist or be managed through companion playbooks:

- PostgreSQL database creation: `playbooks/grafana/create_db.yml`
- PostgreSQL backup: `playbooks/grafana/backup_db.yml`
- PostgreSQL restore: `playbooks/grafana/restore_db.yml`

## Role Task Flow

The role runs the following tasks in order:

1. Update `pg_hba.conf` on the PostgreSQL server to allow password access from the Grafana host IP.
2. Update `pg_hba.conf` on the PostgreSQL server to allow password access from the configured database host IP.
3. Install required OS packages:
   - `adduser`
   - `libfontconfig1`
   - `musl`
4. Download and extract the Grafana tarball into `/opt/`.
5. Create `/opt/grafana` as a symlink to the versioned install directory.
6. Create the Grafana data directory.
7. Create the Grafana log directory.
8. Create the Grafana plugins directory.
9. Create the Grafana PID directory.
10. Create the Grafana provisioning root directory.
11. Create the Grafana provisioning plugins directory.
12. Create the Grafana provisioning datasources directory.
13. Create the Grafana provisioning dashboards directory.
14. Create the Grafana dashboards directory.
15. Render the Prometheus datasource provisioning file.
16. Render the dashboard provider provisioning file.
17. Copy the NGINX Prometheus exporter dashboard.
18. Copy the observability landing dashboard.
19. Copy the node exporter overview dashboard.
20. Copy the node exporter detail dashboard.
21. Create the Grafana configuration directory.
22. Render `defaults.ini`.
23. Render `ldap.toml`.
24. Render the Grafana environment defaults file.
25. Recursively enforce ownership on the Grafana home directory tree.
26. Render the systemd service unit for Grafana.
27. Enable and start the Grafana service.

## Handlers

The role uses these handlers:

- `Restart Grafana`
- `Restart PostgreSQL`
- `Reload systemd daemon`

Grafana restarts are triggered when provisioning files, dashboard JSON files, LDAP config, environment defaults, the systemd unit, or `defaults.ini` change.

## Installation and Layout

Important role defaults and paths:

- Grafana home: `/data/grafana`
- Logs: `/data/grafana/logs`
- Plugins: `/data/grafana/plugins`
- Config: `/data/grafana/conf/defaults.ini`
- LDAP config: `/data/grafana/conf/ldap.toml`
- Provisioning root: `/data/grafana/provisioning`
- Provisioned dashboards directory: `/data/grafana/dashboards`
- Systemd service unit: `/usr/lib/systemd/system/grafana-server.service`

Grafana is installed from the upstream tarball, not from a distro package. The version and edition are controlled through role defaults.

## Dashboard Generation and Provisioning

### Dashboard Source Model

Dashboards in this role are file-based JSON dashboards stored in the role under:

- `roles/grafana_setup/files/dashboards/`

Current dashboard files include:

- `nginx-prometheus-exporter.dashboard.json`
- `observability-landing.dashboard.json`
- `node-exporter-overview.dashboard.json`
- `node-exporter-node-detail.dashboard.json`

These files are copied directly to the target host under:

- `/data/grafana/dashboards`

### Dashboard Provider Configuration

The role renders a Grafana dashboard provisioning file from `provisioning-dashboards.yml.j2` with:

- `apiVersion: 1`
- provider type `file`
- folder name controlled by `grafana_setup_dashboard_folder`
- scan path set to `grafana_setup_dashboards_dir`
- refresh interval controlled by `grafana_setup_dashboard_update_interval_seconds`
- UI editability controlled by `grafana_setup_dashboard_allow_ui_updates`

This means Grafana continuously scans the dashboard directory and imports or refreshes dashboards from disk.

### Home Dashboard

The role sets Grafana’s default home dashboard through `defaults.ini` using:

- `default_home_dashboard_path = {{ grafana_setup_default_home_dashboard_path }}`

In the current configuration, that path points to:

- `/data/grafana/dashboards/observability-landing.dashboard.json`

That makes the observability landing dashboard the expected Grafana home dashboard after deployment and restart.

### Observability Landing Dashboard

The observability landing dashboard is intended to provide a quick operational overview of node state. It includes:

- A summary of tracked nodes
- Count of nodes up
- Count of nodes where the exporter is down
- Count of nodes where the VM is down
- A per-node status grid

Its node availability logic distinguishes between:

- `Up`
- `Exporter Down`
- `VM Down`

The distinction is based on Prometheus data using `up{job="node"}` together with recent presence of `node_time_seconds`, so the dashboard can tell the difference between a dead exporter and a dead VM.

## Prometheus Integration

Prometheus is integrated through Grafana provisioning rather than manual UI setup.

### Datasource Provisioning

The role renders `prometheus.yml` from `provisioning-datasources.yml.j2` into:

- `/data/grafana/provisioning/datasources/prometheus.yml`

The rendered datasource has these characteristics:

- datasource type: `prometheus`
- access mode: `proxy`
- marked as default datasource
- non-editable in the UI
- stable UID from `grafana_setup_prometheus_datasource_uid`

By default the Prometheus URL is built from the first host in the `prometheus` inventory group:

- `http://{{ global_ip_addresses[groups['prometheus'][0]] }}:9090`

### Operational Effect

This gives Grafana an immediately available default Prometheus datasource on startup, which all provisioned dashboards can rely on without manual setup.

### Why This Matters

Because both the datasource and the dashboards are provisioned from files:

- new Grafana hosts can be rebuilt consistently
- dashboards remain version-controlled
- datasource drift through manual UI edits is minimized
- dashboards referencing UID `prometheus` remain stable across redeployments

## PostgreSQL Backend

Grafana is configured to use PostgreSQL as its backend database.

### Runtime Configuration

`defaults.ini` renders the following PostgreSQL connection settings:

- database type: `postgres`
- host: `{{ grafana_setup_pg_host }}:{{ grafana_setup_pg_port }}`
- database name: `{{ grafana_setup_db_name }}`
- username: `{{ grafana_setup_db_user }}`
- password: `{{ grafana_setup_db_password }}`
- SSL mode: `disable`

This backend stores Grafana application state such as:

- users
- dashboards and dashboard metadata
- folders
- permissions
- alerting metadata
- configuration state that Grafana persists internally

### Database Deployment

Database deployment is handled separately from Grafana host deployment through:

- `playbooks/grafana/create_db.yml`

That playbook runs on `pgdb` hosts and applies:

- `global`
- `python3`
- `autofs`

It then imports `roles/grafana_setup/tasks/database.yml`.

The database task file performs these steps:

1. Ensure PostgreSQL is installed.
2. Start and enable PostgreSQL.
3. Ensure `python3-psycopg2` is installed for Ansible PostgreSQL modules.
4. Create the Grafana PostgreSQL user.
5. Create the Grafana PostgreSQL database owned by that user.
6. Create a `.pgpass` entry for password-based access.

In addition, the main Grafana role updates PostgreSQL `pg_hba.conf` so the Grafana host can authenticate to PostgreSQL over the network.

### Database Backup Process

Database backup is handled through:

- `playbooks/grafana/backup_db.yml`

That playbook imports `roles/grafana_setup/tasks/database_backup.yml` on the `pgdb` host.

The backup workflow is:

1. Ensure the backup directory exists.
2. Run `pg_dump` in custom format (`-Fc`) against the Grafana database.
3. Store the output at `grafana_setup_backup_path`.
4. Retain only the newest three backup files.

Default backup location pattern:

- base directory: `{{ grafana_setup_mount_point }}/grafana`
- filename prefix: `grafana_`
- extension: `.sqlc`

This produces timestamped PostgreSQL custom-format backups suitable for `pg_restore`.

### Database Restore Process

Database restore is handled through:

- `playbooks/grafana/restore_db.yml`

The restore process is intentionally split into three phases:

#### 1. Stop Grafana

The playbook first stops the Grafana service on the `grafana` hosts.

#### 2. Restore on PostgreSQL Host

It then imports `roles/grafana_setup/tasks/database_restore.yml` on the `pgdb` host.

That restore task file performs:

1. If no explicit restore path is provided, search the backup directory for `.sqlc` files.
2. Fail if no backups are available.
3. Select the explicitly requested backup, or otherwise the newest available backup.
4. Verify the selected backup file exists.
5. Drop the existing Grafana database.
6. Recreate the Grafana database owned by the Grafana DB user.
7. Run `pg_restore` to load the backup.

#### 3. Start Grafana Again

After restore completes, the playbook starts Grafana again on the `grafana` hosts.

### Backend Operational Notes

This separation between application deployment and database lifecycle is useful because it allows:

- independent database creation
- controlled backups
- safer restore operations with the application stopped
- targeted execution against `pgdb` rather than Grafana hosts

## LDAP Authentication

LDAP is enabled and configured as part of the role.

### Grafana LDAP Enablement

In `defaults.ini`, the role enables LDAP with:

- `[auth.ldap]`
- `enabled = true`
- `config_file = {{ grafana_setup_conf_dir }}/ldap.toml`
- `allow_sign_up = true`
- `skip_org_role_sync = false`

That tells Grafana to load LDAP settings from the rendered `ldap.toml` file.

### LDAP Configuration File

The role renders `ldap.toml` from `roles/grafana_setup/templates/ldap.toml.j2` into:

- `/data/grafana/conf/ldap.toml`

The template configures:

- LDAP server hostname
- LDAP port
- whether SSL is used
- bind DN
- bind password
- user search filter
- user search base DN
- group search filter
- group search base DN
- group-to-role mappings
- LDAP attribute mappings

### LDAP Variables

Important LDAP defaults include:

- `grafana_setup_ldap_server`
- `grafana_setup_ldap_port`
- `grafana_setup_ldap_use_tls`
- `grafana_setup_ldap_bind_dn`
- `grafana_setup_ldap_searchdn`
- `grafana_setup_ldap_searchfilter`
- `grafana_setup_ldap_group_dn`
- `grafana_setup_ldap_editor_group`
- `grafana_setup_ldap_viewer_group`
- `grafana_setup_ldap_group_searchfilter`
- `grafana_setup_ldap_group_searchdn`
- `grafana_setup_ldap_verbose_logging`

The bind password is stored separately in vault-backed role defaults and should not be documented in plaintext.

### Group Mapping Behavior

The role maps LDAP groups to Grafana organization roles as follows:

- `grafana_setup_ldap_group_dn` → `Admin`
- `grafana_setup_ldap_editor_group` → `Editor`
- `grafana_setup_ldap_viewer_group` → `Viewer`

This means role assignment in Grafana is delegated to directory group membership rather than managed manually inside Grafana.

### Attribute Mapping

The template maps standard LDAP attributes to Grafana user fields:

- username → `sAMAccountName`
- surname → `sn`
- email → `userPrincipalName`
- given name → `givenName`

### Operational Effect

With LDAP enabled:

- users authenticate against the configured directory
- Grafana can create users on login if needed
- organization role assignment follows LDAP group membership
- role sync remains active because `skip_org_role_sync = false`

## Configuration Files Rendered by the Role

The role renders these key files:

- `defaults.ini`
  - Main Grafana configuration
  - Includes database, LDAP enablement, dashboard home path, logging, and server settings

- `ldap.toml`
  - LDAP server connection and role mapping rules

- `prometheus.yml`
  - Provisioned Prometheus datasource

- `dashboards.yml`
  - File-based dashboard provider

- environment defaults file
  - Runtime environment variables for the systemd service

- `grafana-server.service`
  - Systemd unit for Grafana

## Restart and Change Behavior

The role notifies handlers when relevant files change.

A change to any of the following causes a Grafana restart:

- datasource provisioning
- dashboard provider provisioning
- dashboard JSON files
- `defaults.ini`
- `ldap.toml`
- Grafana environment defaults
- systemd unit file

A systemd daemon reload also occurs when the systemd service unit changes.

## Suggested Deployment Sequence

A typical full lifecycle for this role is:

1. Run `playbooks/grafana/create_db.yml` to create the PostgreSQL backend.
2. Run `playbooks/grafana/deploy_grafana.yml` to install and configure Grafana.
3. Verify Prometheus datasource provisioning and dashboard availability.
4. Use `playbooks/grafana/backup_db.yml` for routine backups.
5. Use `playbooks/grafana/restore_db.yml` for controlled restore operations.

## Summary

The `grafana_setup` role is structured around file-based, reproducible Grafana configuration:

- Grafana is installed from an upstream tarball.
- Prometheus is provisioned automatically as the default datasource.
- Dashboards are version-controlled JSON files imported from disk.
- The observability landing dashboard is configured as the default home dashboard.
- PostgreSQL is the persistent backend and has separate create, backup, and restore workflows.
- LDAP is enabled for centralized authentication and role mapping.
