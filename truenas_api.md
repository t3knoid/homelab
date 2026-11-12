---
title: "truenas_api"
---

# truenas_api

Idempotently manage TrueNAS objects through the local middleware API.

**Runs on:** the TrueNAS host · **Check mode:** supported in every mode

{{toc}}

---

## Synopsis

Runs on the TrueNAS host and talks to the middleware over its local socket.

Uses `truenas_api_client` when it can be imported, otherwise falls back to `midclt`.

## Modes

| Mode | What it does |
|------|--------------|
| `resource` | Ensures an object exists or does not exist, found via `<namespace>.query`. The lookup must match at most one object. |
| `config` | Manages a singleton configuration (`<namespace>.config` / `<namespace>.update`). |
| `call` | Performs a raw API call (not idempotent unless `read_only=true`). |
| `app` | Reconciles generic catalog/custom Apps with bounded middleware jobs and runtime checks. |
| `vm` | Reconciles TrueNAS virtual machines, their devices, disk zvols and GPU passthrough with bounded middleware jobs and runtime checks. |

> **Note:** Check mode is supported in every mode and never mutates the middleware.

## Comparison and updates

Only keys present in `config` are compared. Lists of scalars compare without regard to order, and ZFS property wrappers (`parsed`/`value`/`rawvalue`) compare case-insensitively against plain values.

Updates send only the changed keys, plus any `companion_keys` and `sensitive_keys` that apply.

**Namespace-specific rules**

- `sharing.smb`: a changed `options` is sent together with `purpose`.
- `sharing.nfs`: setting `maproot_*` clears `mapall_*` and the reverse, because the API treats them as mutually exclusive.

---

## Parameters

### Core

Applies to all modes.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mode` | str | `resource` | Operating mode. One of `resource`, `config`, `call`, `app`, `vm`. |
| `namespace` | str | | API namespace, e.g. `sharing.smb`, `user`, `pool.dataset`, `directoryservices`. |
| `lookup` | dict | `{}` | Equality filters used to find the object (resource mode); required in that mode and must match at most one object. Names are translated by `name_to_id`. |
| `config` | dict | `{}` | Desired state. Only the keys listed here are compared; other attributes are left alone. |
| `state` | str | `present` | Whether the object should exist (resource mode). |
| `id_key` | str | `id` | Attribute holding the object id passed to update/delete. |
| `no_create` | bool | `False` | Fail instead of creating a missing object. |
| `query_options` | dict | `{}` | Second argument passed to `<namespace>.query`. |
| `delete_args` | list | `[]` | Extra arguments passed to `<namespace>.delete` after the id. |
| `job` | bool | `False` | The update (config mode) or call (call mode) is a middleware job; wait for it. |
| `transport` | str | `auto` | Force a transport. `auto` prefers truenas_api_client and falls back to midclt; `client` fails if the client cannot be used. |

### Key handling

Applies to resource and config modes.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `create_only_keys` | list | `[]` | Keys sent on create but never compared or sent on update. |
| `skip_compare_keys` | list | `[]` | Keys never compared (the API returns them in another shape than it accepts them). |
| `sensitive_keys` | list | `[]` | Keys that cannot be read back (passwords). Never compared and redacted from diffs. Sent on create, and on update only if `send_sensitive_on_update` or `send_sensitive_when` applies. |
| `send_sensitive_on_update` | bool | `False` | Send `sensitive_keys` with every update that has other changes. |
| `send_sensitive_when` | list | `[]` | Send `sensitive_keys` with an update only when one of these keys changed. |
| `companion_keys` | dict | `{}` | Map of trigger key to a list of keys. When the trigger key is part of the update payload, the listed keys are sent too, taken from `config`, even if they are unchanged.<br><br>Example `{configuration: [service_type]}` for APIs that require a discriminator next to a nested object. |
| `name_to_id` | dict | `{}` | Map of config/lookup key to `namespace:field`. Names are replaced by ids through `namespace.query`.<br><br>Example `{groups: 'group:name'}`. |

### Call mode

Applies to `mode=call`.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `method` | str | | Method name for `mode=call`. |
| `args` | list | `[]` | Positional arguments for `mode=call`. |
| `read_only` | bool | `False` | `mode=call` only reads data; never reports changed and also runs in check mode. |
| `ignore_error_patterns` | list | `[]` | `mode=call` regular expressions; a matching error is reported as unchanged instead of failing. |

### App mode

Applies to `mode=app`.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `app` | dict | | App definition. See [The `app` definition](#The-app-definition) below. |
| `app_apply` | bool | `False` | Allow app mutations; false plans using read-only queries. Check mode always prevents mutations. |
| `app_job_timeout` | int | `900` | Maximum seconds to wait for each Apps middleware job; a timeout does not cancel the job. |
| `app_health_timeout` | int | `180` | Maximum seconds to wait for each desired Apps runtime state. |
| `app_poll_interval` | int | `5` | Seconds between Apps job and runtime checks. |

#### The `app` definition

Allowed keys are `name`, `source`, `state`, `runtime`, `catalog`, `values`, `compose`, `allow_upgrade` and `allow_delete`; any other key fails.

| Key | Rules |
|-----|-------|
| `name` | Lowercase letters, digits and hyphens. Starts with a letter, ends with a letter or digit, at most 40 characters. |
| `source` | `catalog` or `custom`. |
| `state` | `present` (default) or `absent`. |
| `runtime` | `running` (default) or `stopped`. |
| `catalog` | Catalog apps need `catalog.app`, `catalog.train` and an explicit `catalog.version` other than `latest`. |
| `values` | Optional mapping for catalog apps. Values are merged into the current configuration, so only the listed keys are compared. |
| `compose` | Custom apps need `compose`, a YAML string with a nonempty `services` mapping. It is compared in both directions and replaced as a whole. |
| `allow_upgrade` | Required for a catalog version change, which must be an available upgrade; downgrades are refused. |
| `allow_delete` | Required for deletion. Deletion keeps images and ix volumes. |

> **Note:** Converting an app between catalog and custom, or changing its catalog app or train, is refused. The whole definition is treated as sensitive and hidden from logs.

### VM mode

Applies to `mode=vm`.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `vm` | dict | | Virtual machine definition. See [The `vm` definition](#The-vm-definition) below. |
| `vm_apply` | bool | `False` | Allow VM mutations; false plans using read-only queries. Check mode always prevents mutations. |
| `vm_job_timeout` | int | `900` | Maximum seconds to wait for each VM middleware job; a timeout does not cancel the job. |
| `vm_health_timeout` | int | `180` | Maximum seconds to wait for each desired VM runtime state. |
| `vm_poll_interval` | int | `5` | Seconds between VM job and runtime checks. |

#### The `vm` definition

Extra disks, NICs and other devices already on the VM are never removed. The only device deletions are `cdrom=""` and GPU functions dropped from `gpus`.

Changes to CPU, memory, firmware, clock, security settings or devices on a running VM need a stop and start, which requires `allow_restart`.

The device payload shape is chosen from the TrueNAS version (typed attributes on 25.04 and later).

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| `name` | str | **yes** | | VM name (letters, digits and underscores; at most 40 characters). |
| `description` | str | | `""` | Free-text VM description. |
| `state` | str | | `present` | Whether the VM should exist. |
| `runtime` | str | | `running` | Desired power state when the VM is present. |
| `cpu` | dict | | | CPU topology and affinity settings. See [`vm.cpu`](#vmcpu). |
| `hide_from_msr` | bool | | | Hide hypervisor signatures from guest MSR access. |
| `ensure_display_device` | bool | | | Ensure at least one display device is configured; defaults to false for compatibility with the previous module behavior. |
| `gpus` | list | | | GPU PCI slots selected from `system.advanced.get_gpu_pci_choices`, such as `0000:04:00.0`.<br><br>Each selected GPU expands to all of its PCI functions and is added to the host's isolated GPU list; existing isolation entries are never removed.<br><br>Omit this option to leave PCI devices unmanaged; an explicit empty list removes managed GPU functions from the VM but does not de-isolate them.<br><br>GPUs that use devices critical to the host are refused. |
| `memory_mib` | int | when `state=present` | | Memory in MiB (at least 256). |
| `bootloader` | str | | `UEFI` | Firmware type. |
| `time` | str | | | Guest system clock reference. |
| `enable_secure_boot` | bool | | | Enable UEFI Secure Boot. |
| `trusted_platform_module` | bool | | | Enable a virtual TPM. |
| `shutdown_timeout` | int | | | Seconds to wait for graceful VM shutdown before forcing power off (5–300; default 90). |
| `autostart` | bool | | `False` | Start the VM when TrueNAS boots. |
| `disks` | list | when `state=present` | | Zvol-backed disks. See [`vm.disks[]`](#vmdisks). |
| `nics` | list | when `state=present` | | Network interfaces. See [`vm.nics[]`](#vmnics). |
| `cdrom` | str | | | Install ISO path. An empty string removes the CD-ROM device. |
| `cdrom_order` | int | | | CD-ROM boot order priority (lower numbers boot first); defaults to 1000. |
| `display` | dict | | | Display device. See [`vm.display`](#vmdisplay). |
| `allow_delete` | bool | | `False` | Approve deleting the VM (required for `state=absent`). |
| `allow_restart` | bool | | `False` | Approve stopping and restarting a running VM for changes that need it. Without it, apply fails when a restart is needed. |
| `allow_disk_delete` | bool | | `False` | Also destroy the VM's zvols when deleting it. Otherwise the zvols are kept. |

##### `vm.cpu`

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `vcpus` | int | `1` | Virtual sockets. |
| `cores` | int | `1` | Cores per socket. |
| `threads` | int | `1` | Threads per core. |
| `mode` | str | | CPU virtualization mode. |
| `model` | str | | CPU model when mode is CUSTOM; choices come from `vm.cpu_model_choices`. |
| `cpuset` | str | | Host CPU cores to pin VM CPUs to. |
| `pin_vcpus` | bool | | Pin virtual CPUs to the specified cpuset. |
| `nodeset` | str | | NUMA nodes to constrain VM memory to. |

##### `vm.disks[]`

At least one is required when `state=present`. Missing zvols are created, and a larger `size_gib` grows an existing zvol. Shrinking is refused. The parent dataset of a new zvol must already exist. A zvol may appear only once per VM.

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| `zvol` | str | **yes** | | Zvol path such as `tank/vms/debian12`. |
| `size_gib` | int | **yes** | | Size in GiB. |
| `type` | str | | `VIRTIO` | Disk bus. |
| `sparse` | bool | | `True` | Create the zvol sparse. |
| `disk_sectorsize` | int | | | Logical and physical sector size in bytes. |
| `order` | int | | | Boot order priority (lower numbers boot first); defaults to 1001 for the first disk, then increments in list order. |

##### `vm.nics[]`

At least one is required when `state=present`.

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| `attach` | str | **yes** | | Bridge or interface to attach to. |
| `type` | str | | `VIRTIO` | NIC model. |
| `trust_guest_rx_filters` | bool | | | Trust guest receive filter changes; omitted leaves it unmanaged and TrueNAS defaults to false on create. |
| `mac` | str | | | Fixed MAC address; generated by TrueNAS when omitted. |
| `order` | int | | | Boot order priority (lower numbers boot first); defaults to 1100 for the first NIC, then increments in list order. |

##### `vm.display`

The display password cannot be read back, so it is sent on create and whenever another display attribute changes.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `type` | str | `SPICE` | Display protocol; use VNC to enable a VNC display. |
| `bind` | str | `0.0.0.0` | Address to bind the console to. |
| `port` | int | | Display port passed to the middleware. |
| `web_port` | int | | Web proxy port; omitted leaves it unmanaged and TrueNAS assigns it on create. |
| `wait` | bool | | Wait for a display client before booting; omitted leaves it unmanaged. |
| `web` | bool | | Enable web access for SPICE; VNC requires false and defaults to false. |
| `resolution` | str | | Console resolution. |
| `password` | str | | Console password; VNC passwords must be 1–8 characters, SPICE passwords at least 8 characters. |
| `order` | int | | Boot order priority (lower numbers boot first); defaults to 1200. |

---

## Examples

### SMB share

{% raw %}
```yaml
- name: SMB share
  truenas_api:
    namespace: sharing.smb
    lookup: {name: media}
    config: {name: media, path: /mnt/tank/media, purpose: DEFAULT_SHARE}
```
{% endraw %}

### Read-only call

{% raw %}
```yaml
- name: Read-only call
  truenas_api:
    mode: call
    method: system.version_short
    read_only: true
  register: ver
```
{% endraw %}

### User with group names resolved to ids

{% raw %}
```yaml
- name: User with group names resolved to ids
  truenas_api:
    namespace: user
    lookup: {username: alice}
    config: {username: alice, full_name: Alice, password: "{{ vault_alice_password }}", smb: true, groups: [media]}
    create_only_keys: [password]
    sensitive_keys: [password]
    send_sensitive_when: [smb]
    name_to_id: {groups: "group:name"}
```
{% endraw %}

### Singleton configuration

{% raw %}
```yaml
- name: Singleton configuration
  truenas_api:
    mode: config
    namespace: network.configuration
    config: {nameserver1: 192.168.1.10}
```
{% endraw %}

### Middleware job, ignoring a known no-op error

{% raw %}
```yaml
- name: Middleware job, ignoring a known no-op error
  truenas_api:
    mode: call
    method: update.run
    job: true
    args: [{reboot: false}]
    ignore_error_patterns: ["(?i)no update"]
```
{% endraw %}

### Plan a custom app

{% raw %}
```yaml
- name: Plan a custom app (set app_apply to make changes)
  truenas_api:
    mode: app
    app:
      name: example-web
      source: custom
      compose: |
        services:
          web:
            image: nginx:1.27
    app_apply: false
```
{% endraw %}

### Plan a VM

{% raw %}
```yaml
- name: Plan a VM (set vm_apply to make changes)
  truenas_api:
    mode: vm
    vm:
      name: debian12
      memory_mib: 4096
      disks: [{zvol: tank/vms/debian12, size_gib: 40}]
      nics: [{attach: br0}]
    vm_apply: false
```
{% endraw %}

---

## Return values

| Key | Returned | Type | Description |
|-----|----------|------|-------------|
| `action` | resource/config | str | created, updated, deleted or none (resource/config mode). |
| `changed_keys` | resource/config | list | Keys that differ from the desired state. |
| `id` | resource | raw | Id of the object. Not returned for a planned create in check mode. |
| `diff` | resource/config, when changed | dict | Before and after values of the changed keys; sensitive keys are redacted on create. |
| `result` | call, unless check mode skipped the call or an error was ignored | raw | API return value (call mode). |
| `msg` | call, when applicable | str | Explanation when a call was skipped in check mode or an error was ignored. |
| `ignored_error` | call, when an error was ignored | str | The middleware error that matched `ignore_error_patterns`. |
| `name` | app/vm | str | App or VM name. |
| `actions` | app/vm | list | Planned or applied actions in execution order.<br><br>App actions are `create`, `update`, `upgrade`, `delete`, `start` and `stop`.<br><br>VM actions include `create_zvol:<zvol>`, `grow_zvol:<zvol>`, `isolate_gpu:<pci_slot>`, `stop`, `create`, `update`, `<op>_device:<dtype>`, `delete`, `delete_zvols` and `start`. |
| `planned` | app/vm | bool | True when nothing was applied (check mode, or `app_apply`/`vm_apply` false). |
| `runtime_state` | app/vm | str | Runtime state after reconciliation, or the current state when planned; `ABSENT` when the app or VM does not exist. |
| `approval_required` | app (upgrade/delete) and vm | raw | For apps, true when the planned upgrade or delete lacks its approval.<br><br>For VMs, the list of missing approvals, such as `allow_restart` or `allow_delete`. |
| `device_changes` | vm, when the VM exists | list | Per-device operations with `operation`, `dtype`, `id` and, for updates, the before/after value of each differing attribute or order. Display passwords are excluded. |

