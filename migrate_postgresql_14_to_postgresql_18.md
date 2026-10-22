---
title: "️ Migrate PostgreSQL 14 to PostgreSQL 18"
---

# 🗄️ Migrate PostgreSQL 14 to PostgreSQL 18

This is a same-VM Debian/Ubuntu cluster migration using `pg_upgradecluster --method=dump`. It retains PostgreSQL 14 for recovery and moves the application port to PostgreSQL 18.

Use the dedicated [14-to-18 migration playbook](https://github.com/t3knoid/ansible/blob/main/playbooks/postgresql/migrate_postgresql_14_to_18.yml).

Commands below are operational steps, not an unattended script. Stop on any failed check. Examples use cluster `main`, application port `5432`, source `/data/pgdata`, and target `/data/pgdata18`; replace them with the verified layout. Keep writers stopped until validation finishes.

## ⚙️ Migration Inputs

| Playbook Variable                   | Default              | What to Supply                                                               |
| ----------------------------------- | -------------------- | ---------------------------------------------------------------------------- |
| `postgresql_migrate_host`           | Required; no default | One exact inventory hostname for the VM currently running PostgreSQL 14      |
| `postgresql_migrate_confirm`        | `false`              | Set to `true` only after completing the maintenance and backup prerequisites |
| `postgresql_migrate_cluster`        | `main`               | Existing Debian/Ubuntu cluster name                                          |
| `postgresql_migrate_port`           | `5432`               | Current source/application port; the target must take the same port          |
| `postgresql_migrate_source_dir`     | `/data/pgdata`       | Actual source directory whose `PG_VERSION` is `14`                           |
| `postgresql_migrate_target_dir`     | `/data/pgdata18`     | New, unused target directory with an existing writable parent                |
| `postgresql_migrate_extra_packages` | `[]`                 | PostgreSQL 18 extension packages required by the source databases            |

These are inputs to this migration playbook, not `postgresql_setup_*` deployment settings. The playbook does not automatically derive its paths, port, or extension list from the ordinary setup role's inventory variables. It refuses check mode and existing target clusters/directories; it is not an idempotent deployment or a safe blind-retry operation.

## 📋 1. Prepare

- Obtain an approved maintenance window. Stop all application writers, workers, scheduled jobs, replication/subscription writers, and deployment automation.
- Use an independent controller. Do not launch through Semaphore if its database is on the VM being migrated.
- Verify an independent backup by restoring it on an isolated instance. Rehearse this migration and application validation before production cutover.
- Review PostgreSQL 15, 16, 17, and 18 compatibility changes, not just version 18 release notes. Logical migration does not inherently require intermediate major-version upgrades.
- Inventory extensions in every database, preload libraries, collations/locales, authentication/TLS, tablespaces, FDWs, replication, jobs, and application compatibility. Identify all required PostgreSQL 18 extension packages and supported extension upgrade paths.
- Check free space for the retained source, target cluster, dumps, WAL, temporary files, and external tablespaces. Provision the target parent on the intended filesystem with write access for `postgres`.
- Keep console/SSH administrator access. Pause automatic package upgrades and concurrent package/deployment operations during this procedure.

## 🔎 2. Verify the Source and Target

On the database VM, set these values in the current shell. Keep the values consistent with the playbook inputs you will supply on the controller; exporting these shell variables on the VM does not configure Ansible:

{% raw %}
```bash
export PG_CLUSTER=main
export PG_PORT=5432
export PG_SOURCE=/data/pgdata
export PG_TARGET=/data/pgdata18
sudo pg_lsclusters
sudo cat "$PG_SOURCE/PG_VERSION"
sudo test ! -e "/etc/postgresql/18/$PG_CLUSTER"
sudo test ! -e "$PG_TARGET"
sudo test ! -L "$PG_TARGET"
sudo test -d "$(dirname "$PG_TARGET")"
sudo -u postgres test -w "$(dirname "$PG_TARGET")"
df -h "$PG_SOURCE" "$(dirname "$PG_TARGET")" /var/backups
```
{% endraw %}

Require source `PG_VERSION` to be `14`, the expected source cluster to exist, and both target configuration/data paths to be absent. Inspect existing targets rather than deleting them to make a retry succeed. Check space on external tablespace filesystems separately.

If the source is stopped, start only the verified version 14 cluster for backup and inspection. Omit the start command if already running:

{% raw %}
```bash
sudo pg_ctlcluster 14 "$PG_CLUSTER" status
sudo pg_ctlcluster 14 "$PG_CLUSTER" start
```
{% endraw %}

Inspect the source using its version-specific client:

{% raw %}
```bash
sudo -u postgres /usr/lib/postgresql/14/bin/psql -X --no-password -p "$PG_PORT" -d postgres -v ON_ERROR_STOP=1 -c "SELECT current_setting('server_version_num'), current_setting('data_directory'), current_setting('port'), current_setting('config_file'), current_setting('hba_file');"
sudo -u postgres /usr/lib/postgresql/14/bin/psql -X --no-password -p "$PG_PORT" -d postgres -v ON_ERROR_STOP=1 -c "SELECT datname, usename, application_name, client_addr, state FROM pg_stat_activity WHERE backend_type = 'client backend' ORDER BY datname, usename;"
```
{% endraw %}

Confirm server major 14, the exact source directory, and the original application port. Confirm all writers, including background jobs, remain stopped. Use approved local authentication or a private password file; do not put database passwords in arguments or connection URIs.

## ▶️ 3. Run the Migration From the Controller

Before running, record extension versions in each database, representative row counts/queries, ownership/grants, tablespaces, and application credential checks. The playbook records database/role names, not a complete application-data baseline. Retain the independently verified off-VM backup required in step 1.

On the independent Ansible controller, run from the repository root. Replace the host and inventory with the actual version 14 VM; `pg-1` is not assumed to run PostgreSQL 14:

{% raw %}
```bash
export DB_INVENTORY=inventory/pg/inventory.ini
export DB_HOST='<verified-postgresql-14-hostname>'
ansible-playbook -i "$DB_INVENTORY" playbooks/postgresql/migrate_postgresql_14_to_18.yml -e "postgresql_migrate_host=$DB_HOST" --syntax-check
ansible-playbook -i "$DB_INVENTORY" playbooks/postgresql/migrate_postgresql_14_to_18.yml -e "postgresql_migrate_host=$DB_HOST" --list-hosts
```
{% endraw %}

Require exactly the intended inventory hostname. For the default layout and no additional extension packages, execute only after all preparation is complete:

{% raw %}
```bash
ansible-playbook -i "$DB_INVENTORY" playbooks/postgresql/migrate_postgresql_14_to_18.yml -e "postgresql_migrate_host=$DB_HOST" -e postgresql_migrate_confirm=true -K
```
{% endraw %}

Use the controller's Ansible executable and usual vault/SSH/become options. Confirmation means downtime, stopped writers/automation, an independently verified restore, disk-space checks, and extension compatibility are already addressed. `--check` is deliberately refused. Membership in `pgdb` is not required, but the host must be one exact inventory hostname, not a group or wildcard.

For a different layout or required extensions, prepare a reviewed variable file with the complete inputs and pass it with `-e @YOUR_VARIABLE_FILE.yml` instead of the inline extra variables:

{% raw %}
```yaml
postgresql_migrate_host: YOUR_VERIFIED_HOST
postgresql_migrate_confirm: true
postgresql_migrate_cluster: main
postgresql_migrate_port: 5432
postgresql_migrate_source_dir: /data/pgdata
postgresql_migrate_target_dir: /data/pgdata18
postgresql_migrate_extra_packages: []
```
{% endraw %}

Replace `YOUR_VERIFIED_HOST` and other example values before use, and add required extension packages to the list. From the controller, substitute the actual reviewed variable-file path in these commands:

{% raw %}
```bash
ansible-playbook -i "$DB_INVENTORY" playbooks/postgresql/migrate_postgresql_14_to_18.yml -e @YOUR_VARIABLE_FILE.yml --syntax-check
ansible-playbook -i "$DB_INVENTORY" playbooks/postgresql/migrate_postgresql_14_to_18.yml -e @YOUR_VARIABLE_FILE.yml --list-hosts
ansible-playbook -i "$DB_INVENTORY" playbooks/postgresql/migrate_postgresql_14_to_18.yml -e @YOUR_VARIABLE_FILE.yml -K
```
{% endraw %}

The final command performs the migration because the reviewed variable file contains confirmation. Run it only during the approved outage. Syntax checking and host listing neither connect to the database to verify its layout nor prove extensions or backups are usable. Do not use `--start-at-task`, tags, or step-skipping to bypass the playbook's assertions and backups.

Add every required PostgreSQL 18 extension package to `postgresql_migrate_extra_packages`; the playbook does not reuse an inventory's custom `postgresql_setup_packages_to_install` list. The target parent must already exist and be writable by `postgres`. Source version/data-directory/port mismatches and existing targets are rejected; reruns intentionally refuse a successfully migrated or partially created target.

### 💾 What the Playbook Does

1. Requires explicit confirmation on one Debian/Ubuntu host and verifies unused target paths, a writable parent, and PostgreSQL 14 source data.
2. Starts the source if needed and verifies its live major version, directory, and application port.
3. Saves a private cluster dump, version 14 configuration archive, and `baseline.json` under `/var/backups/postgresql/14-<cluster>-<timestamp>`.
4. Installs PostgreSQL 18 prerequisites through only the package tasks, suppressing package-created clusters/service starts and restoring the original cluster-creation setting in an `always` block.
5. Stops version 14 and executes `pg_upgradecluster --method=dump -v 18 14 <cluster> <target-directory>`. The utility manages the migration/startup sequence; the old cluster remains available for recovery.
6. Verifies version 14 is stopped and version 18 has the expected directory, original application port, database names, and retained roles, allowing new built-in roles.
7. Rebuilds optimizer statistics and reports cluster state and the backup directory. Writers remain your responsibility and must stay stopped for application validation.

The fresh on-VM backup is not automatically copied off-host or restore-tested. It does not capture external configuration or establish application correctness. Do not initialize the target manually, copy the version 14 data directory, run the manual migration command as an extra step, or interrupt/rerun the playbook blindly after failure.

## ✅ 4. Validate and Resume

Return to the database VM, not the controller. If this is a new SSH session, restore the `PG_CLUSTER`, `PG_PORT`, and `PG_TARGET` shell variables from step 2 using the actual playbook inputs before running these commands:

{% raw %}
```bash
sudo pg_lsclusters
sudo cat "$PG_TARGET/PG_VERSION"
sudo pg_ctlcluster 14 "$PG_CLUSTER" status
sudo pg_ctlcluster 18 "$PG_CLUSTER" status
sudo -u postgres /usr/lib/postgresql/18/bin/psql -X --no-password -p "$PG_PORT" -d postgres -v ON_ERROR_STOP=1 -c "SELECT current_setting('server_version_num'), current_setting('data_directory'), current_setting('port'), current_setting('config_file'), current_setting('hba_file');"
sudo -u postgres /usr/lib/postgresql/18/bin/psql -X --no-password -p "$PG_PORT" -d postgres -v ON_ERROR_STOP=1 -c "SELECT datname FROM pg_database ORDER BY datname;"
sudo -u postgres /usr/lib/postgresql/18/bin/psql -X --no-password -p "$PG_PORT" -d postgres -v ON_ERROR_STOP=1 -c "SELECT rolname FROM pg_roles ORDER BY rolname;"
```
{% endraw %}

Require version 18 at the exact target directory and original application port, and version 14 stopped. The version 14 status command is expected to report stopped with a nonzero status; do not interpret that as a reason to start it. If version 18 is not running, inspect logs/configuration before explicitly starting it. Never start both clusters on the application port.

The playbook already compares database/role names and rebuilds statistics. For independent review, inspect `baseline.json` in the exact backup directory printed by the playbook, not a newly generated timestamp path. That directory also contains `cluster.sql` and `configuration.tar.gz`; treat them as sensitive backup artifacts, not scripts to execute against the migrated cluster. Review PostgreSQL built-in role changes separately. Validate application credentials, extensions, representative row counts/queries, ownership/grants, tablespaces, collations, authentication/TLS, jobs, and replication. A successful dump/restore and matching names do not prove application correctness. Follow extension-specific upgrade and collation/index remediation guidance rather than blindly accepting warnings.

Update only the affected host or inventory's variables after successful validation, using the actual target path:

{% raw %}
```yaml
postgresql_setup_version: 18
postgresql_setup_data_dir: /data/pgdata18
```
{% endraw %}

Keep one definition per key and leave shared defaults/unrelated hosts unchanged. Do not rerun normal setup to apply these inventory values: it deletes the default versioned directory and edits `pg_hba.conf` under the data directory, whereas migrated Debian/Ubuntu clusters normally use `/etc/postgresql/18/<cluster>`. Align future automation with the actual `config_file`/`hba_file` paths before re-enabling it.

Resume writers only after application validation and approval. Take an independent PostgreSQL 18 backup and verify monitoring and scheduled backup targets afterward.

## 🧹 Remove PostgreSQL 14

Run commands individually, inspect their results, and stop on unexpected output. Inspection commands are read-only; the explicitly marked cluster deletion and optional package removal are destructive.

### 🔎 1. Verify the Live and Legacy Clusters

In an administrative session on the database VM, set the verified cluster name and live PostgreSQL 18 port. The two clusters are assumed to share the same cluster name after migration; adjust inspection commands if your layout differs:

{% raw %}
```bash
export LEGACY_CLUSTER=main
export PG18_PORT=5432
hostname
sudo pg_lsclusters
sudo pg_conftool --short 14 "$LEGACY_CLUSTER" show data_directory
sudo pg_conftool --short 18 "$LEGACY_CLUSTER" show data_directory
sudo pg_ctlcluster 14 "$LEGACY_CLUSTER" status
sudo -u postgres /usr/lib/postgresql/18/bin/psql -X --no-password -p "$PG18_PORT" -d postgres -v ON_ERROR_STOP=1 -c "SELECT current_setting('server_version_num'), current_setting('data_directory'), current_setting('port'), current_setting('config_file');"
```
{% endraw %}

Confirm the correct VM, PostgreSQL 18 running at the intended directory/port, and PostgreSQL 14 stopped. A stopped-status return from the version 14 command is expected, not a reason to start it. If it is running, stop this procedure and investigate its consumers; do not force-stop and delete it. If legacy configuration or data is already missing, inspect the partial state manually rather than substituting recursive file deletion.

### 💾 2. Verify Data Paths and External Storage

Record the legacy path returned above. Set these variables only after the inspection commands succeed:

{% raw %}
```bash
export PG14_DATA="$(sudo pg_conftool --short 14 "$LEGACY_CLUSTER" show data_directory)"
export PG18_DATA="$(sudo -u postgres /usr/lib/postgresql/18/bin/psql -X --no-password -p "$PG18_PORT" -d postgres -v ON_ERROR_STOP=1 -At -c 'SHOW data_directory;')"
sudo readlink -e "$PG14_DATA"
sudo readlink -e "$PG18_DATA"
sudo cat "$PG14_DATA/PG_VERSION"
sudo cat "$PG18_DATA/PG_VERSION"
sudo ls -la "$PG14_DATA/pg_tblspc"
sudo ls -ld "$PG14_DATA/pg_wal"
sudo ls -la "$PG18_DATA/pg_tblspc"
sudo ls -ld "$PG18_DATA/pg_wal"
```
{% endraw %}

Require nonempty, distinct canonical paths and `PG_VERSION` values `14` and `18` respectively. Neither data directory may contain the other. The old path must match the retained source from the migration record; the live path may be `/data/pgdata18`, `/data/postgresql/pgdata18`, or another verified location. Do not assume a path from an old inventory example is correct.

If `pg_tblspc` contains links or `pg_wal` is a symlink, resolve their targets and review both clusters' storage layout before deletion. `pg_dropcluster` removes associated data, WAL, and tablespace directories. Do not proceed until you have established that no deleted location is used by PostgreSQL 18 or another retained workload. Do not delete tablespace parents or shared mounts manually.

Confirm independent backups are outside every path that will be deleted, their restore test is recorded, and the retention/deletion approval is complete. This is the last point to defer cleanup and retain the old cluster.

### 🗑️ 3. Manually Remove the Approved Legacy Cluster

Recheck cluster state immediately before executing the deletion:

{% raw %}
```bash
sudo pg_lsclusters
sudo pg_ctlcluster 14 "$LEGACY_CLUSTER" status
```
{% endraw %}

Once all preceding checks and approvals are satisfied, the following command permanently removes the selected version 14 cluster:

{% raw %}
```bash
sudo pg_dropcluster 14 "$LEGACY_CLUSTER"
```
{% endraw %}

This deletes legacy cluster data, configuration, logs, and associated WAL/tablespace storage; it is not reversible without suitable backups. Deliberately omit `--stop` so the tool normally refuses a cluster that is still running. Do not replace it with `rm -rf`, delete a whole `/data` tree, or add force-stop options merely to bypass an error. Migration backup directories and version 18 data must remain outside the deletion scope verified above.

### ✅ 4. Verify PostgreSQL 18 and Retain Backups

{% raw %}
```bash
sudo pg_lsclusters
sudo test ! -e "/etc/postgresql/14/$LEGACY_CLUSTER"
sudo test ! -e "$PG14_DATA"
sudo -u postgres /usr/lib/postgresql/18/bin/psql -X --no-password -p "$PG18_PORT" -d postgres -v ON_ERROR_STOP=1 -c "SELECT current_setting('server_version_num'), current_setting('data_directory'), current_setting('port');"
```
{% endraw %}

Confirm the selected version 14 cluster/configuration/data are gone and the same PostgreSQL 18 cluster remains healthy. Test actual application access, monitoring, and backups. If a removal or verification command fails, inspect the actual state instead of repeating deletion blindly. Cleanup does not restore deleted data; preserve evidence and use the approved recovery plan if needed.

Keep migration dumps, configuration archives, and independent backups according to their own retention policy. Do not delete them merely because the old cluster was removed. Ensure server inventory and future backup/provisioning jobs refer to version 18 and its actual paths.

### 📦 5. Optionally Remove Version 14 Packages

Package removal is a separate manual decision after cluster cleanup. First verify that no other version 14 cluster or client workflow needs the packages, then simulate removal:

{% raw %}
```bash
sudo pg_lsclusters
sudo apt-get --simulate remove postgresql-14 postgresql-client-14
```
{% endraw %}

Review the complete proposed removals, including dependencies and extension packages. Do not continue if PostgreSQL 18, shared cluster-management tooling, or required consumers would be affected. Once package removal is independently approved:

{% raw %}
```bash
sudo apt-get remove postgresql-14 postgresql-client-14
```
{% endraw %}

Review any version-specific extension packages separately. Do not remove `postgresql-common`, broadly purge `postgresql*`, or blindly autoremove dependencies. Verify PostgreSQL 18 and application access again after package removal.

## 🛠️ Failure or Rollback

Keep writers and automation stopped. Inspect on the VM:

{% raw %}
```bash
sudo pg_lsclusters
sudo tail -n 100 "/var/log/postgresql/postgresql-18-${PG_CLUSTER}.log"
sudo pg_conftool 14 "$PG_CLUSTER" show data_directory
sudo pg_conftool 14 "$PG_CLUSTER" show port
sudo pg_conftool 18 "$PG_CLUSTER" show data_directory
sudo pg_conftool 18 "$PG_CLUSTER" show port
```
{% endraw %}

Only inspect version 18 paths if that cluster exists; logs may be configured elsewhere and can contain sensitive data. The playbook restores `createcluster.conf` when the package block exits normally or fails, but abrupt controller/process interruption may need manual inspection. Do not delete partial targets, blindly rerun migration, or run normal deployment to repair a failed migration.

Before version 18 accepts application writes, rollback can use the retained version 14 cluster. Verify its configured directory and `PG_VERSION=14`, inspect actual cluster states, and reserve an unused alternate port for version 18. Example only, assuming cluster `main`, original port `5432`, unused alternate `5433`, and a present/running version 18 cluster:

{% raw %}
```bash
sudo pg_ctlcluster 18 main stop
sudo pg_conftool 18 main set port 5433
sudo pg_conftool 14 main set port 5432
sudo pg_ctlcluster 14 main start
sudo pg_lsclusters
```
{% endraw %}

Replace names/ports as required. Omit version 18 commands if no target exists, and omit its stop command if already stopped. Prevent version 18 from unexpectedly restarting during recovery. Restore affected inventory to version 14 and its actual directory, review the old cluster's manual startup setting, and validate application access before resuming writers.

After version 18 accepts application writes, version 14 is stale: switching back loses those writes without a separate reconciliation/restore plan. Do not assume a version 18 dump can be restored into 14. Retain version 14, its packages/configuration, and independent backups through the agreed rollback period. Old-cluster deletion is a separate explicit operation.

## 📚 References

- [PostgreSQL 14-to-18 migration playbook](https://github.com/t3knoid/ansible/blob/main/playbooks/postgresql/migrate_postgresql_14_to_18.yml).
- [Related PostgreSQL 17-to-18 automation](https://github.com/t3knoid/ansible/blob/main/playbooks/postgresql/migrate_postgresql_17_to_18.yml), for comparison only.
- [PostgreSQL 18 upgrading guidance](https://www.postgresql.org/docs/18/upgrading.html).
- [Debian pg_upgradecluster manual](https://manpages.debian.org/testing/postgresql-common/pg_upgradecluster.1.en.html); check the version installed on the VM as well.
- [Debian pg_dropcluster manual](https://manpages.debian.org/testing/postgresql-common/pg_dropcluster.1.en.html).


