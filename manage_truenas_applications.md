---
title: "Manage TrueNAS Applications"
---

# 📦 Manage TrueNAS Applications

Use [deploy_truenas_apps.yml](https://github.com/t3knoid/ansible/blob/main/playbooks/truenas/deploy_truenas_apps.yml) for an isolated Apps workflow in the existing `truenas` role. It does not run the NAS configuration stages from [configure_truenas.yml](https://github.com/t3knoid/ansible/blob/main/playbooks/truenas/configure_truenas.yml). The NAS workflow does not automatically invoke this new entry point either.

TrueNAS should own the app lifecycle through its middleware. Do not run `docker_setup`, the ordinary Docker service deployment role, or ad hoc Docker Compose commands on the appliance to bypass Apps management.

This workflow manages any catalog app supported by the installed TrueNAS release or any compatible custom Compose app. Application-specific settings belong in catalog `values` or custom `compose`; no database-specific behavior is embedded in deployment. Middleware contracts were checked against the TrueNAS 25.10 API and upstream implementation. Automated verification uses mocked middleware, not a live NAS deployment.

## 📋 Prerequisites

- Confirm the installed TrueNAS release and supported catalog/custom Apps settings. The role checks middleware readiness, the minimum supported version (25.10 by default), and initial administrator setup before reading the Apps pool configuration.
- Configure the Apps storage pool through an approved workflow, and confirm capacity, storage health, and administrator recovery access.
- Create dedicated persistent datasets and establish the container's required UID/GID and permissions. Review the dataset and raw permission-call guidance in the [contributor guide](../contrib/truenas-role-contributor-guide.md).
- Reserve app ports, review network restrictions, pin approved versions, and establish resource limits, health checks, backup policy, and recovery procedures.
- Keep credentials in the encrypted host vault and preserve `truenas_no_log: true`. Do not put real secrets in CLI extra variables, plaintext Compose files, or published plans.

## 📝 Inventory Interface

Add `truenas_apps` to the existing NAS host-variable directory under `inventory/truenas/host_vars/truenas-01/`. Keep the list in one file and preserve other entries; an empty list is the default and makes no middleware calls. This is an Ansible-facing contract translated into TrueNAS API payloads. Replace every placeholder before applying.

{% raw %}
```yaml
truenas_apps_mode: plan
truenas_apps:
  - name: catalog-example
    source: catalog
    state: present
    catalog:
      app: "<verified-catalog-app-name>"
      train: "<verified-catalog-train>"
      version: "<approved-catalog-version>"
    values: {}

  - name: custom-web
    source: custom
    state: present
    runtime: running
    compose: |
      services:
        web:
          image: nginx:<approved-image-tag>
          ports:
            - "8080:80"
```
{% endraw %}

The examples illustrate independent catalog and custom apps. Catalog app/train/version and `values` must match the selected catalog schema; obtain them from the TrueNAS UI/API rather than assuming settings are portable between catalog entries. Custom Compose can include services, bind mounts, environment variables, networks, resource controls, and health checks accepted by TrueNAS. Pin approved image tags or digests and manage intentional changes through inventory. The role does not validate image immutability or invent workload-specific defaults.

| Field               | Behavior                                                                                                       |
| ------------------- | -------------------------------------------------------------------------------------------------------------- |
| `truenas_apps_mode` | `plan` by default; `apply` permits mutation unless Ansible check mode is active                                |
| `name`              | Unique lowercase app name, maximum 40 characters, starting with a letter and ending with an alphanumeric       |
| `source`            | Required `catalog` or `custom`                                                                                 |
| `state`             | `present` by default; `absent` requests deletion, requiring explicit approval during apply                     |
| `runtime`           | `running` by default or `stopped`; reconciles the runtime independently of configuration                       |
| `catalog`           | For present catalog apps, requires nonempty string `app`, `train`, and `version`; literal `latest` is rejected |
| `values`            | Managed catalog settings; nested mappings are merged with current values and lists are replaced                |
| `compose`           | Complete custom Compose YAML, parsed as a mapping with a nonempty `services` mapping                           |
| `allow_upgrade`     | Boolean, false by default; required to apply a catalog version change                                          |
| `allow_delete`      | Boolean, false by default; required to delete an existing app                                                  |

Present catalog entries cannot include `compose`; present custom entries cannot include `catalog` or `values`. Absent entries only require identity/source plus any deletion approval. Omission is not deletion. Unknown top-level fields are rejected rather than ignored. Both configuration forms are treated as sensitive. Avoid untrusted Compose content: deployment can access host paths and resources with the privileges TrueNAS grants Apps.

For catalog apps, only supplied values are managed; server defaults and unrelated nested keys are preserved. Lists remain ordered. Custom Compose is compared as a complete structured document, so removing a key from inventory removes it on update; formatting-only changes do not force a deployment. Changing source type, catalog app, or catalog train in place is refused rather than silently replacing an app.

## 🧭 Discover Settings for an Application

The inventory variable is `truenas_apps`. Password variables are separate vault-backed values referenced from an app's settings. Use the following process for each new app; do not reuse another app's `values` keys just because its install form looks similar.

### 🔎 1. Identify the App and Versions

In the TrueNAS UI, open Apps and locate the application in Discover Apps. Record its catalog identifier, train, catalog package version, upstream App Version, minimum supported TrueNAS release, and configuration requirements. Open the installation form to review available settings without submitting installation. Labels and navigation can vary by TrueNAS release.

| Information                               | PostgreSQL Example           | Where It Belongs                                                        |
| ----------------------------------------- | ---------------------------- | ----------------------------------------------------------------------- |
| Instance name you choose                  | `postgres`                   | `truenas_apps[].name`; must match an existing app when adopting it      |
| Catalog identifier, not the display title | `postgres`                   | `catalog.app`                                                           |
| Train                                     | `community`                  | `catalog.train`                                                         |
| Catalog package Version                   | `1.5.39`                     | `catalog.version`, as a quoted string                                   |
| Upstream App Version                      | `18.6-trixie`                | Informational; the package's image choices determine the deployed image |
| Keywords and homepage                     | `database`, `postgresql.org` | Catalog metadata, not extra deployment fields                           |

Do not put `18.6-trixie` in `catalog.version`. A catalog package can offer multiple upstream image families, so also verify the image selection inside `values`. Use an explicit available package version instead of `latest`, and review version-specific warnings before changing an existing installation.

For a read-only lookup, run the following in a private SSH session on the NAS, with root escalation as required:

{% raw %}
```bash
sudo midclt call catalog.get_app_details postgres '{"train":"community"}'
```
{% endraw %}

Replace the identifier and train for another app. Inspect the returned `versions` for the desired package and its schema/support information. The NAS's available catalog and installed-release API are authoritative; a version on GitHub is not proof that it is currently available on your NAS. Do not install an app manually just to discover its settings.

The live response contains both a ready-made configuration template and its resolved schema; start here before reconstructing values from GitHub. If `jq` is available, filter the read-only catalog output in the same private NAS session:

{% raw %}
```bash
sudo midclt call catalog.get_app_details postgres '{"train":"community"}' | jq '.versions | keys'
sudo midclt call catalog.get_app_details postgres '{"train":"community"}' | jq '.versions["1.5.39"] | {version, human_version, healthy, supported, healthy_error, required_features, last_update}'
sudo midclt call catalog.get_app_details postgres '{"train":"community"}' | jq '.versions["1.5.39"].values'
sudo midclt call catalog.get_app_details postgres '{"train":"community"}' | jq '.versions["1.5.39"].schema.questions'
```
{% endraw %}

Replace the version in every filter when selecting another package. `jq` only formats/selects JSON and is not required for deployment; do not install extra packages on the appliance merely for these examples. Without it, inspect those same properties in the original response.

| Response Property                                     | How to Use It                                                                                                            |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `versions["1.5.39"].values`                           | Starting template for that app's `values`; fill required empty fields and review defaults                                |
| `versions["1.5.39"].schema.questions`                 | Resolved types, choices, conditions, limits, and storage/ACL requirements on this NAS                                    |
| Version-level `healthy`, `supported`, `healthy_error` | Check catalog validity and installed-release compatibility; investigate false/error results before deployment            |
| `required_features`                                   | Features such as `normalize/ix_volume` and `definitions/node_bind_ip` used by the catalog schema; not inventory settings |
| `last_update` and top-level `last_update`             | Catalog/package update information, not the time an installed app was deployed or upgraded                               |

The supplied PostgreSQL response reports `healthy: true` and `supported: true` for `1.5.39`. Those are catalog checks, not proof that PostgreSQL is installed, running, reachable, or backed up. Never substitute `latest_version` automatically for the reviewed version pin.

### 📖 2. Read the Selected Version's Schema

Use the returned version's `schema.questions` first: unlike raw catalog files, it includes resolved dynamic definitions such as bind-IP choices and ACL fields for this NAS. For supporting context in the official catalog, inspect `trains/<train>/<app>/<catalog-version>/app.yaml` and `questions.yaml` in the [TrueNAS Apps repository](https://github.com/truenas/apps). For this example, use [PostgreSQL 1.5.39 metadata](https://github.com/truenas/apps/blob/master/trains/community/postgres/1.5.39/app.yaml) and [its questions schema](https://github.com/truenas/apps/blob/master/trains/community/postgres/1.5.39/questions.yaml). Record a commit permalink for change review when reproducible source references matter; the `master` branch can change.

- `app.yaml` identifies `name`, `train`, package `version`, upstream `app_version`, compatibility, and container runtime identity information.
- In `questions.yaml`, use `variable` names as keys, not human-readable `label` or `group` headings. A top-level question's variable becomes a key under `values`.
- For a `schema.type: dict`, follow `attrs` recursively to build nested mappings. For a list, follow `items` to determine whether each element is a scalar or an object.
- Respect types, required fields, enum `value` strings, ranges, and defaults. A required field with a valid default may be populated by middleware; a required password with an empty default still needs a real value.
- Follow `show_if` conditions and `$ref` definitions using the install form and normalized catalog schema when needed. Do not copy schema-control keys such as `attrs`, `$ref`, `required`, or `show_if` into `values`.
- Review storage, networking, resources, and application settings together. Fields and defaults can change between package versions; do not assume the current schema applies to an older pinned package.

### 🧩 3. Map Choices to Inventory Values

**Keep the outer app definition the same; copy the selected version's `.values` object under the app's `values:` key without changing its nesting.** The property names come from that app's response, not from Ansible or the PostgreSQL example.

#### 📦 Example: Add Another Catalog App

First retrieve the new app's configuration template on the NAS. Replace `<app-id>`, `<train>`, and `<version>` with verified catalog values before running:

{% raw %}
```bash
sudo midclt call catalog.get_app_details <app-id> '{"train":"<train>"}' \
  | jq '.versions["<version>"].values'
```
{% endraw %}

Suppose the command returns the following **illustrative** object. These keys are invented to demonstrate the mapping, not settings for a real catalog app:

{% raw %}
```json
{
  "application": { "username": "", "password": "" },
  "network": { "web_port": 8080 },
  "storage": { "data": { "type": "ix_volume" } }
}
```
{% endraw %}

Translate that object into YAML directly beneath `values`. Fill the required empty fields and replace the password with an encrypted vault reference:

{% raw %}
```yaml
truenas_apps:
  - name: another-app
    source: catalog
    state: present
    runtime: running
    catalog:
      app: "<app-id>"
      train: "<train>"
      version: "<version>"
    values:
      application:
        username: chosen-user
        password: "{{ vault_another_app_password }}"
      network:
        web_port: 8080
      storage:
        data:
          type: ix_volume
```
{% endraw %}

In this example, `application`, `network`, and `storage` remain siblings under `values`. If your actual response uses different keys or nesting, preserve those instead. `application` does not have to equal the catalog identifier or instance name. Keep booleans as booleans, numbers as numbers, and lists as lists; do not flatten everything into strings.

| Inventory Location               | Source                                                                                           |
| -------------------------------- | ------------------------------------------------------------------------------------------------ |
| `truenas_apps[].name`            | Instance name you choose; use the installed instance name when adopting an existing app          |
| `truenas_apps[].source`          | `catalog` for this workflow                                                                      |
| `truenas_apps[].catalog.app`     | Catalog identifier supplied to `catalog.get_app_details`, confirmed by the response              |
| `truenas_apps[].catalog.train`   | Selected catalog train                                                                           |
| `truenas_apps[].catalog.version` | Selected package version key under `versions`, not the upstream image version                    |
| `truenas_apps[].values`          | Object returned by `.versions["<version>"].values`, with reviewed overrides and vault references |

To determine valid choices, required fields, and conditional settings for those properties, inspect the same version's schema:

{% raw %}
```bash
sudo midclt call catalog.get_app_details <app-id> '{"train":"<train>"}' \
  | jq '.versions["<version>"].schema.questions'
```
{% endraw %}

Do not copy `schema`, `questions`, `attrs`, descriptions, or catalog metadata into `values`; they explain the payload but are not the payload. Define the referenced secret in encrypted host variables using step 4 below. Review ports, storage, permissions, and defaults before previewing. Append the new app as another `- name:` entry in the existing `truenas_apps` list alongside PostgreSQL, not as a second top-level variable or as a child of PostgreSQL's `values`. No playbook code changes are needed for another supported catalog app.

The generic mapping above applies to every supported catalog app. A separate [PostgreSQL worked example](#-worked-example-postgresql) at the end demonstrates real defaults, chosen overrides, and version-specific storage/resource settings without making those properties part of the generic interface.

### 🔐 4. Define Application Passwords in Vault

Generate a unique password with your approved password manager. If the encrypted host vault exists, edit it from the controller:

{% raw %}
```bash
ansible-vault edit inventory/truenas/host_vars/truenas-01/vault.yml
```
{% endraw %}

If it does not exist, use `ansible-vault create inventory/truenas/host_vars/truenas-01/vault.yml` instead. Use the repository's vault identity/password-file configuration or its usual vault password prompt. Inside the vault editor, add the following key with the actual generated value; this placeholder is not a usable password:

{% raw %}
```yaml
vault_truenas_postgres_password: "<unique-generated-password>"
```
{% endraw %}

Keep the Jinja reference in the unencrypted app definition and the actual secret only in encrypted host variables. A missing vault key causes templating to fail; the deployment does not generate a password automatically. The vault encryption password, NAS SSH/become passwords, and application database password are different credentials. Do not enter secrets into CLI extra variables, commands that print decrypted inventory, tickets, or source-controlled plaintext files.

For another app, choose a distinct vault variable and place its reference at the schema's password/token field. For custom Compose, template secrets from vault into the appropriate configuration without assuming the role provisions external secret files. Vault protects repository storage and `no_log` protects ordinary Ansible output; the app and middleware still need access to the resolved credentials. Updating an app environment/password field does not guarantee rotation of credentials already stored in its data volume; PostgreSQL's initialization password is not an existing-role password-reset workflow.

### 🔍 5. Inspect an Existing App Safely

For adoption or comparison, the following read-only commands run on the NAS. The configuration command can print plaintext secrets; use only a private administrative session with appropriate terminal/log handling. Do not run it through shared CI logs or paste its unredacted output into inventory or support requests.

{% raw %}
```bash
sudo midclt call app.query '["id","=","postgres"]("id","=","postgres".md)'
sudo midclt call app.config postgres
```
{% endraw %}

Replace `postgres` with the installed instance name, not necessarily the catalog identifier. Use query metadata to confirm `custom_app`, catalog name/train, and installed package version. For a catalog app, select the relevant user settings from `app.config` as the starting point for `values`, replace every secret with a vault reference, and compare against the exact package schema. Do not copy runtime metadata, generated context, or the entire `app.query` response into `values`. For a custom app, use the returned Compose configuration to build the complete `compose` YAML instead of catalog `values`.

### ✅ 6. Review and Preview the Result

For custom apps, start with the application's official Compose/image documentation rather than catalog `questions.yaml`. Verify ports, mount destinations, UID/GID, required environment variables, image versions, and health checks, then place the complete compatible Compose document in `compose` with `source: custom`. A catalog app's question names do not automatically translate to Docker environment variables.

Before running the validation commands below, confirm that the app identity/version exists on the NAS catalog, required settings and secrets are populated, ports and storage are approved, and no unintended upgrade or deletion approvals are present. Syntax checks do not prove vault variables exist or API values are valid. Plan/check mode compares against live state but does not submit catalog schema validation or launch containers; apply and workload-level verification remain necessary.

## 🔎 Validate and Preview

Run from the repository root with the usual vault credentials:

{% raw %}
```bash
ansible-playbook -i inventory/truenas/inventory.ini playbooks/truenas/deploy_truenas_apps.yml --limit truenas-01 --syntax-check --ask-vault-pass
ansible-playbook -i inventory/truenas/inventory.ini playbooks/truenas/deploy_truenas_apps.yml --limit truenas-01 --list-tasks --ask-vault-pass
ansible-playbook -i inventory/truenas/inventory.ini playbooks/truenas/deploy_truenas_apps.yml --limit truenas-01 --check --ask-vault-pass
```
{% endraw %}

Omit `--ask-vault-pass` when a configured vault identity/password file already supplies access. Add `-k`/`-K` if SSH/become passwords are required. The Apps entry point has the `truenas_apps` tag. With configured apps, both plan and check mode connect to the NAS for read-only preflight, pool checks, discovery, and current configuration. They report intended actions and approvals without submitting jobs. A planned change may report `changed` even though nothing was applied. Catalog availability, API validation, and actual deployment health are ultimately checked during apply.

## ▶️ Apply Configuration

{% raw %}
```bash
ansible-playbook -i inventory/truenas/inventory.ini playbooks/truenas/deploy_truenas_apps.yml --limit truenas-01 -e truenas_apps_mode=apply --ask-vault-pass
```
{% endraw %}

All declarations are structurally validated before the first deployment. Configured apps are then reconciled sequentially. Catalog apps use `app.create`, `app.config`, and `app.update`; custom apps use structured Compose configuration through the same Apps API. Configuration updates occur only when managed values differ. No direct Docker CLI commands or unrelated NAS configuration stages run.

Keep the list limited to reviewed changes: one failed app stops the remaining deployments, but completed apps are not rolled back. There is no cross-app dependency orchestrator; provide an appropriate list order and perform application-level readiness checks before enabling dependents.

## 🔄 Upgrades and Deletion

### 📋 Exact Catalog Version Behavior

Inventory is desired state, not a record Ansible automatically synchronizes from the UI. For an existing catalog app with the same instance name, catalog identifier, and train, the module compares the installed `app.query` version string with `catalog.version`. It currently checks equality only, not version ordering. Any difference is labeled `upgrade`, including an inventory pin older than the installed version. This label is not proof that the target is newer or that TrueNAS permits the transition.

| Installed State Versus Inventory                            | Plan Mode or Ansible `--check`                                                   | Apply Mode                                                                                                                                                |
| ----------------------------------------------------------- | -------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Same catalog package version                                | Compares managed settings and runtime; no version action                         | Updates differing managed settings and reconciles runtime; otherwise leaves the app unchanged                                                             |
| Different package version, `allow_upgrade` omitted or false | Reports `upgrade` and `approval_required: true`; submits no job                  | Fails before submitting an upgrade or changing that app's settings/runtime                                                                                |
| Different package version, `allow_upgrade: true`            | Reports `upgrade`; submits no job or upgrade-summary request                     | Calls `app.upgrade_summary` for the exact inventory pin; if its `upgrade_version` matches, submits `app.upgrade`                                          |
| Installed version newer than the inventory pin              | Still labels the mismatch `upgrade`; it does not identify a downgrade separately | Without approval, fails as above. With approval, sends the older pin to the TrueNAS upgrade API and relies on TrueNAS to reject an unsupported transition |
| Source type, catalog identifier, or train differs           | Fails rather than planning an automatic conversion                               | Fails rather than replacing/converting the app                                                                                                            |

There is no independent older-version rejection in the current module, and matching `upgrade_summary.upgrade_version` is not a local newer-than check. Do not enable `allow_upgrade` to silence an unexplained mismatch, especially when the app was already upgraded through the UI. Do not describe this workflow as providing a guaranteed downgrade-prevention guard beyond its default approval gate. It does not call `app.rollback`, automatically choose the newest release, or rewrite inventory.

Ansible check mode prevents mutations even when `truenas_apps_mode=apply`. Conversely, setting `allow_upgrade: false` does not mean "ignore version drift and continue configuring": apply stops on that app's mismatch. Earlier apps in the list may already have been changed, and later ones are not processed after the failure.

### ▶️ Perform a Planned Catalog Upgrade

1. Record the installed package version and upstream application version in the TrueNAS UI or the read-only `app.query` output. Confirm which instance is being changed and review its current configuration privately as needed.
2. Verify a recoverable, application-consistent backup and an approved maintenance window. Review release notes, image/data-format migration warnings, and the target package's schema using the discovery steps above. A package upgrade can change the upstream image, defaults, or startup behavior even if you do not edit the image selector.
3. Choose an available newer catalog package version. Update `catalog.version` in the existing app entry and reconcile any changed `values` fields with the new schema. Preserve its name, source, catalog identifier/train, secrets, storage, and other settings unless those changes are explicitly part of the plan.
4. Set `allow_upgrade: true` on that app, not globally for the list. The following is a fragment of the existing app mapping, not a replacement for its complete definition; replace the version placeholder with a verified available version:

{% raw %}
```yaml
allow_upgrade: true
catalog:
  app: postgres
  train: community
  version: "<approved-newer-package-version>"
```
{% endraw %}

5. From the repository root, preview all configured apps on the selected NAS:

{% raw %}
```bash
ansible-playbook -i inventory/truenas/inventory.ini playbooks/truenas/deploy_truenas_apps.yml --limit truenas-01 --check --ask-vault-pass
```
{% endraw %}

6. Confirm only intended actions are proposed, then apply during the approved window:

{% raw %}
```bash
ansible-playbook -i inventory/truenas/inventory.ini playbooks/truenas/deploy_truenas_apps.yml --limit truenas-01 -e truenas_apps_mode=apply --ask-vault-pass
```
{% endraw %}

7. The module checks the upgrade summary, merges managed values into the current configuration, waits for the upgrade job, reconciles requested runtime, and waits for the expected runtime state. Check mode did not execute these steps or validate the target's upgrade compatibility in advance. Do not retry a timed-out job until its actual status is known.
8. Verify the installed version, application/client access, data integrity, and backup operation. After successful verification, remove `allow_upgrade: true` or set it to false, leaving `catalog.version` at the newly installed version. Rerun the preview and review unexpected remaining actions.

`--limit truenas-01` selects the NAS, not a single app. The playbook still processes every entry in that host's `truenas_apps` list; review the whole list and avoid unrelated pending changes during the upgrade. For PostgreSQL, a catalog package upgrade and a database-major/image-family upgrade are distinct concerns; any database migration needs its own compatibility and recovery plan.

### 🔧 Reconcile an Upgrade Performed Through the UI

For example, if inventory pins `1.5.39` but the UI installed a newer package, the next run does not learn the newer version automatically. Default plan mode will report the mismatch, and apply with the default `allow_upgrade: false` will fail. Do not lower the installed version merely to make the old inventory match.

1. Confirm the UI operation completed and the app is healthy. In a private administrative session on the NAS, query the exact installed instance:

{% raw %}
```bash
sudo midclt call app.query '["id","=","postgres"]("id","=","postgres".md)'
```
{% endraw %}

2. Read its installed `version`, `custom_app`, and catalog metadata. Use the installed package version, not the upstream image tag, human-readable combined version, or catalog's latest version. If an upgrade job is still running, resolve that first.
3. Review the newer package's schema, release notes, and current app settings. Decide whether the UI change is approved. If it is, update the existing inventory entry's `catalog.version` to the exact installed version and keep `allow_upgrade` false or absent. Matching the installed version does not require upgrade approval because no version transition is requested.
4. Adopt any approved UI setting changes into the corresponding managed `values` fields and update vault references as appropriate. Otherwise, once the version mismatch is resolved, apply can overwrite those UI settings with the older inventory values. Pay particular attention to storage, image selection, credentials, and fields whose meaning/defaults changed with the package.
5. Run the preview command above. There should be no `upgrade` action once version strings match, though settings or runtime changes can still appear. Review every action before applying; only apply if configuration/runtime reconciliation is intended. Record the inventory reconciliation through the normal repository review process.

If the UI upgrade is not approved, stop and use a separately reviewed, TrueNAS-supported recovery/rollback procedure with compatible data backups. Do not set `allow_upgrade: true` against the stale lower pin as a rollback technique. Reverting the version string alone cannot reverse application data migrations. The code's missing direction check is an implementation safeguard to address separately; inventory reconciliation is the required operational fix for an approved out-of-band upgrade.

### 📝 UI Settings and Custom App Drift

- For a catalog app at the same package version, fields explicitly managed under `values` are authoritative: differing UI settings are restored to inventory on apply. Unspecified nested catalog settings are preserved; managed lists are replaced as lists. Copy approved UI changes into inventory before applying if they should be retained.
- Runtime drift is also managed: an app stopped through the UI can be started again if inventory says `runtime: running`, and the converse applies to `stopped`.
- For custom apps, the entire structured `compose` document is authoritative. A UI image/configuration edit is planned as an `update` and can be reverted to inventory's older image or settings on apply, without an `allow_upgrade` gate. To adopt it, reconcile the full Compose definition first. Image changes can have data-format consequences regardless of this being called an update.
- Pulling a newer image under an unchanged custom tag does not change the declared Compose configuration; the workflow does not compare image digests, automatically pull that tag, or reliably report that image-only drift. Prefer approved immutable image references where supported.

### 🗑️ Delete an App

For retirement, set `state: absent` and review the plan before setting `allow_delete: true`. Deletion keeps `remove_images: false` and `remove_ix_volumes: false`, and does not delete host-path datasets or invoke force-removal options. However, TrueNAS App deletion invokes Compose teardown with Docker-volume removal; Docker-managed named/anonymous volumes may be removed. Prefer dedicated backed-up host-path datasets for data requiring independent retention, and review actual volume ownership and the installed release's deletion behavior before approving removal. Dataset preservation flags do not constitute a backup policy.

## ✅ Job Completion and Health

Every create/update/upgrade/start/stop/delete waits for the middleware job to succeed using `core.get_jobs`. Failed or aborted jobs fail the play; a timeout leaves the job running for operator inspection instead of retrying or cancelling it blindly. Configure `truenas_apps_job_timeout` (default 900 seconds), `truenas_apps_health_timeout` (180), and `truenas_apps_poll_interval` (5) as needed.

Apply then waits for the requested `RUNNING`, `STOPPED`, or absent state using `app.query`, including on otherwise unchanged apps. TrueNAS runtime state incorporates configured container health, but it is not a substitute for a workload-specific API/database/client test. Configure suitable Compose or catalog health checks and verify service connectivity, persistence, authentication, and backups separately. New Apps are created through TrueNAS's normal startup behavior; `runtime: stopped` stops them after creation, not before their first startup.

Results expose only name, planned actions, runtime state, and approval requirements. No config/Compose diff is returned. Keep `truenas_no_log: true`; inspect failed job details privately in TrueNAS because middleware errors may contain secrets.

## 🔧 Troubleshoot Playbook Errors

Stop after a failed deployment and identify the failed stage before retrying. Record the app name, job ID, method, timestamp, and last known state. Earlier apps or configuration changes may already have completed; failure does not roll them back. Keep `truenas_no_log: true` rather than exposing resolved passwords and Compose content to obtain a clearer error.

### 🖥️ 1. Check Controller Configuration and Access

Run these commands from the repository root on the Ansible controller. They do not deploy Apps:

{% raw %}
```bash
ansible-inventory -i inventory/truenas/inventory.ini --graph
ansible-playbook -i inventory/truenas/inventory.ini playbooks/truenas/deploy_truenas_apps.yml --limit truenas-01 --syntax-check --ask-vault-pass
ansible -i inventory/truenas/inventory.ini truenas-01 -m ansible.builtin.ping --ask-vault-pass
ansible -i inventory/truenas/inventory.ini truenas-01 -b -m ansible.builtin.command -a 'id -u' --ask-vault-pass
```
{% endraw %}

`ping` tests the Ansible SSH/module connection, not ICMP. The become check should return UID `0`. Use `-k` for the inventory user's SSH password and `-K` for its become password if needed; use the established vault identity instead of `--ask-vault-pass` when configured. Do not disable host-key checking or grant extra privileges just to bypass a connection failure. A syntax check does not establish API compatibility or validate secrets.

### 🔎 2. Retrieve the Failed Middleware Job

When Ansible reports an error such as `app.create job 91418 ended in FAILED`, run the following in an existing private administrative SSH session on the NAS. Replace `91418` with the job ID from your failure:

{% raw %}
```bash
sudo midclt call core.get_jobs '["id","=",91418]("id","=",91418.md)' '{"select":["id","method","state","error"]}'
```
{% endraw %}

This omits job arguments/results, which may contain resolved secrets. The `error` field can still contain sensitive text: inspect it locally and redact it before sharing. For an empty result, confirm the NAS and ID; the job may no longer be retained. Use the TrueNAS UI Jobs view and retained logs rather than assuming the operation never occurred.

To identify recent Apps lifecycle jobs when the ID is unknown:

{% raw %}
```bash
sudo midclt call core.get_jobs '["method","in",["app.create","app.update","app.upgrade","app.start","app.stop","app.delete"]("method","in",["app.create","app.update","app.upgrade","app.start","app.stop","app.delete".md)]' '{"select":["id","method","state","error"],"order_by":["-id"],"limit":10}'
```
{% endraw %}

`FAILED` or `ABORTED` requires diagnosis. `RUNNING` or `WAITING` means the operation may still be active, including after an Ansible timeout; do not launch a competing create/upgrade or cancel it blindly. Inspect progress through the UI. These are read-only queries, not retry commands.

### 🩺 3. Check NAS Readiness and App State

Run these read-only checks on the NAS; replace `postgres` with the installed instance name:

{% raw %}
```bash
sudo midclt call system.ready
sudo midclt call system.version_short
sudo midclt call user.has_local_administrator_set_up
sudo midclt call docker.config
sudo midclt call app.query '["id","=","postgres"]("id","=","postgres".md)' '{"select":["id","state","version","custom_app"]}'
sudo midclt call app.ip_choices
sudo midclt call app.used_ports
```
{% endraw %}

Readiness and initial-administrator checks should be true, the release must meet the role minimum, and `docker.config` must identify an Apps pool. The role does not configure that pool automatically. An empty app query means no matching app is currently reported; inspect the failed job and storage before concluding there are no partial resources. A runtime state such as `CRASHED`, `DEPLOYING`, or `STOPPED` is different from catalog `healthy`/`supported` metadata.

For resource/startup failures, inspect the Apps UI container logs. On releases that provide the lifecycle log, inspect its recent entries privately:

{% raw %}
```bash
sudo tail -n 100 /var/log/app_lifecycle.log
sudo zfs list -o name,used,avail,mountpoint
sudo ss -ltnp
```
{% endraw %}

These can help identify image-pull/startup errors, missing paths, exhausted storage, or listening-port conflicts. Log locations and available diagnostics vary by release. Avoid collecting entire logs unnecessarily: application logs and process details can expose credentials or user data. Do not edit files under `/mnt/.ix-apps`, reset dataset permissions recursively, delete volumes, or run direct Docker lifecycle commands as a troubleshooting shortcut.

### 🧩 4. Match the Error to Its Configuration Field

| Error or Symptom                                                          | Diagnostic and Next Action                                                                                                                                                                                                                                                      |
| ------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `[EINVAL] network.tcp_port.host_ips.0: Input should be '0.0.0.0' or '::'` | Inspect the selected version's resolved bind-IP enum and `app.ip_choices`. This exact failure occurred with the NAS-specific IP. Use only a supported binding after approval; `0.0.0.0` listens across all IPv4 interfaces, so review firewall/client access before changing it |
| Port already in use                                                       | Compare inventory with `app.used_ports` and `ss` output; choose an approved unused host port or resolve its legitimate owner without stopping unrelated services                                                                                                                |
| Invalid/missing catalog setting or version                                | Inspect `catalog.get_app_details` for the exact app/train/version and its `.values`/`.schema.questions`; fill required fields and use enum values, not UI labels                                                                                                                |
| Missing vault variable or authentication failure                          | Confirm the correct encrypted host variables are loaded. Do not print the password; application credentials, SSH/become credentials, and vault encryption credentials are distinct                                                                                              |
| Storage permission denied or missing path                                 | Inspect the configured storage branch, actual path, capacity, and catalog run-as UID/GID. Correct only the intended dataset's policy; do not recreate or wipe data to retry initialization                                                                                      |
| Catalog version mismatch or approval required                             | Follow the upgrade/UI reconciliation procedure above. Do not add `allow_upgrade: true` merely to silence a stale older pin                                                                                                                                                      |
| Job timeout                                                               | Query the same job ID first. Increase `truenas_apps_job_timeout` only after assessing progress and expected runtime; increasing it does not fix a failed validation                                                                                                             |
| Health timeout after a successful job                                     | Check app/container state and logs, ports, dependencies, and workload-level readiness. Configuration may already be installed; increasing `truenas_apps_health_timeout` does not repair a crashed app                                                                           |

To inspect PostgreSQL's selected package settings again, without installing anything:

{% raw %}
```bash
sudo midclt call catalog.get_app_details postgres '{"train":"community"}'
```
{% endraw %}

For installed settings, `sudo midclt call app.config postgres` is read-only but may print plaintext secrets. Use it only under the private-session precautions in the existing-app inspection section; do not paste its output into a ticket or enable Ansible secret logging.

### ✅ 5. Preview Before Retrying

After correcting the identified cause, confirm that no previous job is still active and review partial app/data state. From the controller, explicitly force a non-mutating preview even if host variables set `truenas_apps_mode: apply`:

{% raw %}
```bash
ansible-playbook -i inventory/truenas/inventory.ini playbooks/truenas/deploy_truenas_apps.yml --limit truenas-01 -e truenas_apps_mode=plan --check --ask-vault-pass
```
{% endraw %}

Review every app's proposed actions, not just the one that failed. This preview does not submit `app.create`/`app.upgrade` or prove that catalog validation/startup will succeed. Retry using the documented apply command only after review and approval, then verify application access and data. Do not delete a partially created app or its storage solely to make a rerun start fresh; preserve data and establish the recovery plan first.

## 🧪 Offline Tests

The [local fixture](../../roles/truenas/tests/apps.yml) validates declarations without NAS credentials or access. The [unit tests](../../roles/truenas/tests/test_apps.py) exercise catalog/custom lifecycle decisions, job failures/timeouts, approvals, idempotence, check mode, and runtime checks with mocked middleware:

{% raw %}
```bash
ansible-playbook -i localhost, roles/truenas/tests/apps.yml
python -m unittest discover -s roles/truenas/tests -p test_apps.py -v
```
{% endraw %}

## 🛠️ Recovery and Workload Configuration

After failure, inspect actual app configuration, middleware jobs, and storage before retrying. A health timeout can follow a successfully installed configuration; reverting inventory does not reverse data migrations performed by the app. Recovery may require restoring app configuration and a compatible backup together. Automatic application/data rollback is intentionally not attempted.

Keep workload configuration and migration separate from deployment. For PostgreSQL, for example, manage database roles, databases, extensions, access policy, and backups through a separate database workflow; imports/cutovers are not part of this generic task. The same separation applies to application-specific setup for any other catalog or custom app.

## 🐘 Worked Example: PostgreSQL

This example applies the generic discovery process to `postgres` from the `community` train, catalog package `1.5.39`. The package advertises upstream App Version `18.6-trixie`; these are different version identifiers. All properties below are specific to this package and must not be assumed to exist for another app.

### 🔎 Extract the Default Configuration

On the NAS, retrieve the selected version's defaults:

{% raw %}
```bash
sudo midclt call catalog.get_app_details postgres '{"train":"community"}' \
  | jq '.versions["1.5.39"].values'
```
{% endraw %}

The `postgres` part of that object is:

{% raw %}
```json
{
  "image_selector": "v18_image",
  "user": "",
  "password": "",
  "database": "",
  "shm_size_mb": 256,
  "additional_envs": []
}
```
{% endraw %}

Copy this object under `truenas_apps[].values.postgres`, preserving the property names. Its siblings in the full response, such as `resources`, `network`, and `storage`, stay beside `postgres` under `values`; they are not nested inside it.

### 📝 Distinguish Defaults From Choices

| Setting                               | Catalog Default      | Choice in This Example                    | Reason                                                                  |
| ------------------------------------- | -------------------- | ----------------------------------------- | ----------------------------------------------------------------------- |
| `catalog.version`                     | Selected package key | `"1.5.39"`                                | Pin the reviewed catalog package, not the image tag                     |
| `values.postgres.image_selector`      | `v18_image`          | `v18_image`                               | Retain the package's PostgreSQL 18 selection                            |
| `values.postgres.user`                | Empty                | `postgres`                                | Supply a nonempty initial database account; not a NAS user              |
| `values.postgres.password`            | Empty                | `"{{ vault_truenas_postgres_password }}"` | Supply the required password through encrypted host variables           |
| `values.postgres.database`            | Empty                | `postgres`                                | Supply a nonempty initial database name                                 |
| `values.postgres.shm_size_mb`         | `256` MB             | `512` MB                                  | Illustrative override within the schema's `64`–`2048` MB range          |
| `values.resources.limits.cpus`        | `2` CPUs             | `4` CPUs                                  | Illustrative container CPU limit, not dedicated cores                   |
| `values.resources.limits.memory`      | `4096` MB            | `8192` MB                                 | Illustrative container memory limit, not a reservation                  |
| `values.network.tcp_port.port_number` | `5432`               | `5432`                                    | Retain the default host port after checking availability                |
| `values.network.tcp_port.host_ips`    | `[]`                 | `["0.0.0.0"]`                             | Explicit approved IPv4 wildcard; requires firewall/client-access review |
| `values.storage.data.type`            | `ix_volume`          | `ix_volume`                               | Retain local TrueNAS-managed data storage                               |

The username/database names and resource sizing are choices, not conclusions inferred from metadata. Shared memory (`/dev/shm`), total container memory, and PostgreSQL `shared_buffers` are separate controls. These resource overrides are not recommendations for every workload and do not change [the NAS inventory](../../inventory/truenas/host_vars/truenas-01/default.yml) automatically. Omitted optional lists such as `additional_envs` need not be managed when unused.

### 📦 Assemble the Inventory Entry

Merge approved settings into the existing app entry; do not create a duplicate top-level `truenas_apps` variable:

{% raw %}
```yaml
truenas_apps:
  - name: postgres
    source: catalog
    state: present
    runtime: running
    catalog:
      app: postgres
      train: community
      version: "1.5.39"
    values:
      postgres:
        image_selector: v18_image
        user: postgres
        password: "{{ vault_truenas_postgres_password }}"
        database: postgres
        shm_size_mb: 512
      resources:
        limits:
          cpus: 4
          memory: 8192
      network:
        host_network: false
        tcp_port:
          bind_mode: published
          port_number: 5432
          host_ips:
            - "0.0.0.0"
      storage:
        data:
          type: ix_volume
          ix_volume_config:
            acl_enable: false
            dataset_name: data
```
{% endraw %}

Define `vault_truenas_postgres_password` in the encrypted host vault before previewing. Use the generic validation/apply procedure earlier in this runbook, with the same job/error checks and approval rules used for any other app.

### 🛡️ Check PostgreSQL-Specific Constraints

- Confirm supported image selections using the exact version's schema. This package offers PostgreSQL 16/17/18 and pgvector variants; changing image families on initialized data requires the catalog's migration guidance and verified backups, not just an inventory edit.
- Initial account/password/database values do not automatically update roles or databases in an existing data directory. Use a separate database configuration/password-reset workflow after initialization.
- The supplied NAS schema advertises only `0.0.0.0` and `::` as bind-IP choices; a NAS-specific IP was rejected. Wildcard binding is not a client allow-list. Review current schema, firewall access, and port conflicts before applying.
- The catalog run-as identity is UID/GID `999:999`. Host labels such as `netdata` and `docker` do not represent database credentials. Review numeric ownership for a host path; do not create host accounts or add unsupported UID/GID fields to match those labels.
- ixVolume is local managed storage, not an SMB/NFS export or an independent backup. If selecting the alternative `host_path` branch, prepare its path and permissions first and do not combine both storage branches. Do not use NFS for PostgreSQL's live data directory.
- Review conditional ACL settings before enabling them: the supplied ixVolume ACL branch defaults its `options.force` to true. The example leaves ACL setup disabled and does not recursively change permissions on existing data.
- Inspect the schema for optional environment variables, additional storage, labels, and advanced networking rather than copying settings from another app. CPU/memory limits have no explicit range in the supplied schema; size them against actual NAS capacity.
- Only explicitly supplied values are managed. Omitting a previously managed property does not necessarily restore its default; specify an intentional desired value when changing a current setting.

## 📚 API References

- [TrueNAS 25.10 Apps API](https://api.truenas.com/v25.10/api_methods_app.html)
- [Create/update/delete and upgrade schemas](https://github.com/truenas/middleware/blob/TS-25.10.0/src/middlewared/middlewared/api/v25_10_0/app.py)
- [Upstream lifecycle and deletion behavior](https://github.com/truenas/middleware/blob/TS-25.10.0/src/middlewared/middlewared/plugins/apps/crud.py)
