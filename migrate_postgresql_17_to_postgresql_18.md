---
title: "Migrate PostgreSQL 17 to PostgreSQL 18"
---

# Migrate PostgreSQL 17 to PostgreSQL 18

This runbook details on migrating a database from PostgesSQL 17 to 18. It uses Debian/Ubuntu `pg_upgradecluster --method=dump`, leaves version 17 intact, and keeps the application port on version 18. It does not initialize or delete existing data directories.

Defaults: cluster `main`, port `5432`, source `/data/pgdata`, target `/ansible/pgdata18`. The target directory and `18/main` must not already exist. A rerun intentionally refuses existing targets, including a successfully migrated cluster.

## 1. Prepare

- Schedule downtime. Stop all database writers, workers, scheduled jobs, and deployment automation. Keep them stopped until application validation passes.
- Verify an independent backup by restoring it on an isolated instance. The playbook also takes a fresh dump and configuration backup, but does not prove
  that dump can be restored or copy it off the database host.
- Check PostgreSQL 18 release notes and extension compatibility. Supply required version 18 extension packages through `postgresql_migrate_extra_packages`.
- Check free space for the new cluster, backups under `/var/backups/postgresql`, temporary files, WAL, and any external tablespaces. Provision the target parent
  directory on the intended filesystem and make it writable by `postgres`.

On the database host, confirm the layout:

{% raw %}
```bash
sudo pg_lsclusters
sudo cat /data/pgdata/PG_VERSION
df -h /data /ansible
sudo -u postgres test -w /ansible
```
{% endraw %}

## 2. Run From The Controller

Run from this repository using an Ansible controller that does not depend on the database being migrated. In particular, do not run through Semaphore backed by that database. For `ansible-0`:

{% raw %}
```bash
ansible-playbook \
  -i inventory/ansible/inventory.ini \
  playbooks/postgresql/migrate_postgresql_17_to_18.yml \
  -e postgresql_migrate_host=ansible-0 \
  -e postgresql_migrate_confirm=true \
  -K
```
{% endraw %}

Use your controller's Ansible executable and usual vault/become options. The host must be one explicit inventory hostname; membership in `pgdb` is not required. `postgresql_migrate_confirm=true` confirms that **all preparation steps above are complete**, not merely permission to run. Check mode is deliberately unsupported.

For a different layout, pass these variables as needed:

{% raw %}
```yaml
postgresql_migrate_host: YOUR_HOST
postgresql_migrate_confirm: true
postgresql_migrate_cluster: main
postgresql_migrate_port: 5432
postgresql_migrate_source_dir: /data/pgdata
postgresql_migrate_target_dir: /ansible/pgdata18
postgresql_migrate_extra_packages: []
```
{% endraw %}

Pass a variable file with `-e @YOUR_VARIABLE_FILE.yml`. The playbook installs the standard server/client dependencies plus these extra packages, not an inventory's custom `postgresql_setup_packages_to_install` list. Include every required extension package explicitly.

The playbook checks the source, starts it if necessary, saves a private backup, installs version 18 without package-created clusters or service starts, restores the original package cluster-creation setting, stops version 17, migrates, and rebuilds statistics. It verifies the new version, directory, port, database names, and role names. No Ctrl+C or step-mode task selection is needed.

## 3. Validate And Resume

Keep writers stopped. Check application connections using actual application credentials, extensions in each database, representative row counts, and important queries. Review authentication, tablespaces, scheduled jobs, and replication if used. Basic playbook checks do not replace these application checks.

Update only the affected inventory's group or host variables to match the live cluster:

{% raw %}
```yaml
postgresql_setup_version: 18
postgresql_setup_data_dir: /ansible/pgdata18
```
{% endraw %}

For `ansible-0`, use [inventory/ansible/group_vars/all/main.yml](../inventory/ansible/group_vars/all/main.yml). Keep one definition per key. Do not change role defaults for this migration.
Resume writers only after validation, then take an independent version 18 backup.

Do **not** rerun the normal setup role just to apply these inventory values: it deletes the default versioned directory and edits `pg_hba.conf` under the data directory, whereas migrated Debian/Ubuntu clusters normally use configuration under `/etc/postgresql`. That behavior has not been changed by this playbook.

## 🧹 Remove PostgreSQL 17

Run commands individually, inspect their results, and stop on unexpected output. Inspection commands are read-only; the explicitly marked cluster deletion and optional package removal are destructive.

### 🔎 1. Verify the Live and Legacy Clusters

In an administrative session on the database VM, set the verified cluster name and live PostgreSQL 18 port. The two clusters are assumed to share the same cluster name after migration; adjust inspection commands if your layout differs:

{% raw %}
```bash
export LEGACY_CLUSTER=main
export PG18_PORT=5432
hostname
sudo pg_lsclusters
sudo pg_conftool --short 17 "$LEGACY_CLUSTER" show data_directory
sudo pg_conftool --short 18 "$LEGACY_CLUSTER" show data_directory
sudo pg_ctlcluster 17 "$LEGACY_CLUSTER" status
sudo -u postgres /usr/lib/postgresql/18/bin/psql -X --no-password -p "$PG18_PORT" -d postgres -v ON_ERROR_STOP=1 -c "SELECT current_setting('server_version_num'), current_setting('data_directory'), current_setting('port'), current_setting('config_file');"
```
{% endraw %}

Confirm the correct VM, PostgreSQL 18 running at the intended directory/port, and PostgreSQL 17 stopped. A stopped-status return from the version 14 command is expected, not a reason to start it. If it is running, stop this procedure and investigate its consumers; do not force-stop and delete it. If legacy configuration or data is already missing, inspect the partial state manually rather than substituting recursive file deletion.

### 💾 2. Verify Data Paths and External Storage

Record the legacy path returned above. Set these variables only after the inspection commands succeed:

{% raw %}
```bash
export PG17_DATA="$(sudo pg_conftool --short 17 "$LEGACY_CLUSTER" show data_directory)"
export PG18_DATA="$(sudo -u postgres /usr/lib/postgresql/18/bin/psql -X --no-password -p "$PG18_PORT" -d postgres -v ON_ERROR_STOP=1 -At -c 'SHOW data_directory;')"
sudo readlink -e "$PG17_DATA"
sudo readlink -e "$PG18_DATA"
sudo cat "$PG17_DATA/PG_VERSION"
sudo cat "$PG17_DATA/PG_VERSION"
sudo ls -la "$PG17_DATA/pg_tblspc"
sudo ls -ld "$PG17_DATA/pg_wal"
sudo ls -la "$PG17_DATA/pg_tblspc"
sudo ls -ld "$PG17_DATA/pg_wal"
```
{% endraw %}

Require nonempty, distinct canonical paths and `PG_VERSION` values `17` and `18` respectively. Neither data directory may contain the other. The old path must match the retained source from the migration record; the live path may be `/data/pgdata18`, `/data/postgresql/pgdata18`, or another verified location. Do not assume a path from an old inventory example is correct.

If `pg_tblspc` contains links or `pg_wal` is a symlink, resolve their targets and review both clusters' storage layout before deletion. `pg_dropcluster` removes associated data, WAL, and tablespace directories. Do not proceed until you have established that no deleted location is used by PostgreSQL 18 or another retained workload. Do not delete tablespace parents or shared mounts manually.

Confirm independent backups are outside every path that will be deleted, their restore test is recorded, and the retention/deletion approval is complete. This is the last point to defer cleanup and retain the old cluster.

### 🗑️ 3. Manually Remove the Approved Legacy Cluster

Recheck cluster state immediately before executing the deletion:

{% raw %}
```bash
sudo pg_lsclusters
sudo pg_ctlcluster 17 "$LEGACY_CLUSTER" status
```
{% endraw %}

Once all preceding checks and approvals are satisfied, the following command permanently removes the selected version 14 cluster:

{% raw %}
```bash
sudo pg_dropcluster 17 "$LEGACY_CLUSTER"
```
{% endraw %}

This deletes legacy cluster data, configuration, logs, and associated WAL/tablespace storage; it is not reversible without suitable backups. Deliberately omit `--stop` so the tool normally refuses a cluster that is still running. Do not replace it with `rm -rf`, delete a whole `/data` tree, or add force-stop options merely to bypass an error. Migration backup directories and version 18 data must remain outside the deletion scope verified above.

### ✅ 4. Verify PostgreSQL 18 and Retain Backups

{% raw %}
```bash
sudo pg_lsclusters
sudo test ! -e "/etc/postgresql/17/$LEGACY_CLUSTER"
sudo test ! -e "$PG17_DATA"
sudo -u postgres /usr/lib/postgresql/18/bin/psql -X --no-password -p "$PG18_PORT" -d postgres -v ON_ERROR_STOP=1 -c "SELECT current_setting('server_version_num'), current_setting('data_directory'), current_setting('port');"
```
{% endraw %}

Confirm the selected version 17 cluster/configuration/data are gone and the same PostgreSQL 18 cluster remains healthy. Test actual application access, monitoring, and backups. If a removal or verification command fails, inspect the actual state instead of repeating deletion blindly. Cleanup does not restore deleted data; preserve evidence and use the approved recovery plan if needed.

Keep migration dumps, configuration archives, and independent backups according to their own retention policy. Do not delete them merely because the old cluster was removed. Ensure server inventory and future backup/provisioning jobs refer to version 18 and its actual paths.

### 📦 5. Optionally Remove Version 17 Packages

Package removal is a separate manual decision after cluster cleanup. First verify that no other version 14 cluster or client workflow needs the packages, then simulate removal:

{% raw %}
```bash
sudo pg_lsclusters
sudo apt-get --simulate remove postgresql-17 postgresql-client-17
```
{% endraw %}

Review the complete proposed removals, including dependencies and extension packages. Do not continue if PostgreSQL 18, shared cluster-management tooling, or required consumers would be affected. Once package removal is independently approved:

{% raw %}
```bash
sudo apt-get remove postgresql-17 postgresql-client-17
```
{% endraw %}

Review any version-specific extension packages separately. Do not remove `postgresql-common`, broadly purge `postgresql*`, or blindly autoremove dependencies. Verify PostgreSQL 18 and application access again after package removal.

## Failure Or Rollback

On any failure, keep writers and automation stopped. Inspect `sudo pg_lsclusters` and `/var/log/postgresql/postgresql-18-main.log`. Do not blindly rerun, remove a target, or execute the normal deployment playbook. Migration failure can leave a partial target; this playbook never deletes it or automatically rolls back.

Before version 18 has accepted writes, rollback is possible using the retained version 17 cluster. Inspect its configured directory and verify `PG_VERSION` is
`17`. If version 18 exists and is running, stop it, then assign it an unused port before restoring version 17 to the original application port. Example only, assuming `5432` was the original port and `5433` is otherwise unused:

{% raw %}
```bash
sudo pg_ctlcluster 18 main stop
sudo pg_conftool 18 main set port 5433
sudo pg_conftool 17 main set port 5432
sudo pg_ctlcluster 17 main start
```
{% endraw %}

Omit target commands if that cluster was never created, or its stop command if already stopped. Restore inventory to version 17 and its actual directory, review the old cluster's manual startup setting, and validate application access before resuming writers. After version 18 accepts writes, version 17 is stale: switching back loses those writes and requires a separate reconciliation/restore plan.

Retain version 17 and independent backups through the agreed rollback period. Old-cluster deletion is a separate, explicit operation, not part of this playbook.