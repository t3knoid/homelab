---
title: "Provision a Virtual Machine Runbook"
---

# 🏃 Provision a Virtual Machine Runbook

This runbook describes provisioning a new Ubuntu 24.04 virtual machine using [playbooks/provision_vm.yml](../playbooks/provision_vm.yml), or preparing an already installed baremetal host using the corresponding post-install stages.

VM provisioning clones an existing Proxmox cloud-init template, migrates it to the requested node, applies hardware and network settings, starts the guest, waits for cloud-init, removes the cloud-init drive, and reboots. The remaining stages bootstrap Python, join Active Directory, apply the Ansible node baseline, provision users, and prepare disks.

**Important: The full playbook includes potentially destructive disk preparation. It is not a general-purpose hardware-update playbook. Do not run it blindly against existing machines.**

## 💻 1. Login to an Ansible Control Node

{% raw %}
```shell
cd ~/ansible
source /opt/python_3.12/bin/activate
INV=inventory/test/inventory.ini
HOST=test-01
```
{% endraw %}

Replace the inventory and hostname with the intended values. Run commands from the control node, which must reach Proxmox, Pi-hole, Active Directory, and the target host/network. Confirm Ansible, the required collections, and their Python dependencies are installed in the activated environment.

## 📥 2. Pull the Latest Code

{% raw %}
```shell
git status --short
git pull --ff-only origin main
```
{% endraw %}

Preserve or resolve local changes before pulling. Use the repository's branch and review process where applicable.

## 🛡️ 3. Confirm Prerequisites and Recovery Options

Before creating a VM, confirm:

- An existing, tested Proxmox cloud-init template matches `global_os[vms_os].template`. For `ubuntu_24_server`, the configured name is `ubuntu-server-24.04-cloudinit`. See the [template creation runbook](create_proxmox_vm_template.md).
- The source template and target node support the required clone/migration operations. The Ansible-native clone requests a full clone with `qcow2` format on `vms_config.storage`; use storage that supports this.
- The target node's `local` storage supports snippets. The role writes user/network data into `/var/lib/vz/snippets` and references it as `local:snippets/...`.
- The control node has SSH and privilege escalation access to the Proxmox target node. Its hostname must resolve.
- Runtime or vault configuration supplies the required Proxmox API password/token settings, Pi-hole API authentication, cloud-init user/password settings, and `ad_administrator_password`. Do not commit secrets in plaintext.
- Domain DNS is reachable and configured appropriately for domain discovery and joining. Hostnames must resolve from the control node and managed hosts.
- SSH access to the guest uses the intended account. Cloud-init adds the control node's generated RSA public key to `global_vm_template_user`; do not assume the control node's current username is that account.
- There are no conflicting hostnames or IPs. Preserve existing entries when editing the global address map.
- You have backups and a recovery plan for any existing machine or disk that might be affected.

This workflow is currently Ubuntu-specific: the Python bootstrap hardcodes the Ubuntu `noble` repository. Selecting another `vms_os` does not make the full provisioning process compatible with arbitrary operating systems.

## ⚙️ 4. Define the Host and VM Configuration

### Inventory Groups

Add the new host to the intended [inventory](../inventory/test/inventory.ini):

{% raw %}
```ini
[vms]
test-01 vms_proxmox_node=pve-1

[python]
test-01

[linux]
test-01
```
{% endraw %}

`vms` selects VM creation and the later configuration stages. `python` selects Python bootstrap. `linux` follows the repository's normal inventory pattern but is not itself required by the top-level provisioning playbook. `vms_clone` is deprecated and ignored; omit it.

### Global IP Mapping

Add the hostname and a unique address under the existing `global_ip_addresses` mapping in [roles/global/vars/main.yml](../roles/global/vars/main.yml). Do not replace the whole mapping. Select a free address in the intended subnet and check it against the existing map and network reservations.

`global_ip_address` is derived from this map. The current VM network template uses interface `ens18`, a `/24` prefix, and `global_gateway` (which defaults to the subnet's `.1` address). Confirm these assumptions fit the selected template, bridge, and VLAN before deployment.

### Host or Group Variables

Create a host-specific variables file under the selected inventory, or use shared variables like [inventory/test/group_vars/all/main.yml](../inventory/test/group_vars/all/main.yml). A minimal example for the Ansible-native path is:

{% raw %}
```yaml
vms_config:
  cores: "2"
  sockets: "1"
  cpu: host
  memory: 1024
  ostype: l26
  storage: local
  disk_os:
    disk: virtio0
    size: 20
  nic0:
    model: virtio
    bridge: vmbr0

vms_os: ubuntu_24_server
vms_use_terraform: false
vms_additional_packages: []
python3_version: "3.12"
```
{% endraw %}

`disk_os` is optional when no boot-disk resize is needed. A requested size must not shrink the existing disk. `python3_version` defaults to `3.12`; defining it explicitly documents intent but is not mandatory.

### Active Parameter Reference

These descriptions apply to the Ansible-native provisioning path:

| Setting                                                           | Current behavior                                                                        |
| ----------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| `vms_proxmox_node`                                                | Destination node for migration, snippet creation, and later VM operations.              |
| `vms_os`                                                          | Selects the template name from `global_os`.                                             |
| `vms_config.storage`                                              | Clone storage; cloning requests `qcow2`.                                                |
| `cores`, `sockets`, `cpu`, `memory`, `ostype` within `vms_config` | Applied during cloud-init VM configuration. Memory is in MB.                            |
| `vms_config.disk_os.disk`, `.size`                                | Device and requested total size in GB for boot-disk expansion.                          |
| `vms_config.nic0` or `.network.nic0`                              | NIC model, bridge, and optional VLAN `tag`. The nested form takes precedence.           |
| `vms_config.net0`                                                 | Raw Proxmox network string overriding the structured NIC settings.                      |
| `vms_config.disk2`                                                | Optional additional disk; define `storage`, with optional `disk`, `size`, and `backup`. |
| `vms_additional_packages`                                         | Packages added to the global package list for first-boot cloud-init.                    |

The current path does **not** apply `vms_autoinstall`, `vms_enable_serial_terminal`, `vms_config.boot_order`, `vms_config.scsihw`, or `vms_config.disk_os.storage`, `.format`, and `.backup` as requested configuration. It clones an already installed image, enables the guest-agent option when cloning, configures serial console unconditionally, and sets `bootdisk` to `virtio0`. Verify inherited template settings rather than assuming every inventory field is applied.

Terraform-backed provisioning is selected by `vms_use_terraform: true`. Its hardware handling differs; the table above is not a Terraform parameter guarantee. This runbook's example explicitly uses the Ansible-native path.

## 💾 5. Review Disk Preparation Before Execution

The final [disk stage](../playbooks/vms/prep_disk.yml) applies the [disks role](../roles/disks/tasks/main.yml) to both VMs and baremetal hosts.

Its discovery is not limited to `vms_config.disk2`. It selects disks without child partitions, attempts to create GPT/ext4 partitions, discovers unmounted ext4 partitions, and may rewrite `/etc/fstab`. A disk without partitions is not necessarily empty: it may contain a whole-disk filesystem or valuable data.

`disks_disk_mounts` defaults to an empty list. This does **not** disable partitioning/formatting. Declaring `disk2` creates the virtual disk but does not by itself supply a mount configuration.

For an existing reachable host, inspect disks before proceeding:

{% raw %}
```shell
ansible "$HOST" -i "$INV" -b -m ansible.builtin.command \
  -a 'lsblk -o NAME,TYPE,SIZE,FSTYPE,MOUNTPOINT,UUID'
```
{% endraw %}

Review intended mount definitions, owners, and groups. The role uses a nested combination of configured mounts and discovered unmounted ext4 partitions, not explicit per-device assignments. Do not assume it safely maps several mountpoints to several disks.

Use the full playbook only when all attached disks are understood and this behavior is acceptable. For existing hosts, baremetal, or uncertain storage, use the staged procedure in step 7 and review disk preparation separately. If you need selective or non-destructive disk handling, change and validate the role before running it; there is no documented safe skip flag in this workflow.

## 📝 6. Commit and Validate Configuration

Commit only your intended inventory and address changes:

{% raw %}
```shell
git add inventory/test/
git add roles/global/vars/main.yml
git commit -m "Configure provisioning for test-01"
git push origin main
```
{% endraw %}

Replace paths and names as appropriate. Check the staged diff before committing, especially if there are unrelated local changes.

{% raw %}
```shell
ansible-inventory -i "$INV" --graph
ansible-playbook -i "$INV" playbooks/provision_vm.yml --limit "$HOST" --list-hosts
ansible-playbook -i "$INV" playbooks/provision_vm.yml --limit "$HOST" --syntax-check
```
{% endraw %}

Syntax checks do not establish storage safety or prove runtime credentials and connectivity. Confirm the selected host is present in every required stage's group.

## 🚀 7. Provision the VM or Run Selected Stages

### Full New-VM Workflow

Only after accepting the disk-stage behavior and completing the prerequisite checks:

{% raw %}
```shell
ansible-playbook -i "$INV" playbooks/provision_vm.yml --limit "$HOST"
```
{% endraw %}

Add `-k` for SSH password prompting, `-K` for become password prompting, and the repository's required vault options when applicable. Set the intended SSH user through the existing connection configuration or `-u`.

Do not reuse the full workflow as a routine hardware-update command. It performs DNS changes, VM configuration, domain configuration, reboots, and disk preparation. An existing VM is not cloned again, but other stages still run, and the original provisioning run removes its cloud-init drive.

### Staged Workflow Without Automatic Disk Preparation

For a new VM, run the creation stage first; skip this command for baremetal:

{% raw %}
```shell
ansible-playbook -i "$INV" playbooks/vms/provision_vm.yml --limit "$HOST"
```
{% endraw %}

After the OS is installed and SSH is reachable, run the post-install stages explicitly:

{% raw %}
```shell
ansible-playbook -i "$INV" playbooks/python/bootstrap_python3.yml --limit "$HOST"
ansible-playbook -i "$INV" playbooks/ad/join_domain.yml --limit "$HOST"
ansible-playbook -i "$INV" playbooks/ansible/prep_ansible_node.yml --limit "$HOST"
ansible-playbook -i "$INV" playbooks/vms/add_users.yml --limit "$HOST"
```
{% endraw %}

Inspect disks using step 5. Run the following only after deliberately approving the disk role's scope and mount behavior:

{% raw %}
```shell
ansible-playbook -i "$INV" playbooks/vms/prep_disk.yml --limit "$HOST"
```
{% endraw %}

## 🌐 8. Baremetal OS Installation Uses PXE First

The top-level provisioning playbook does not create a physical machine or install its OS. If an OS already exists, use the staged post-install workflow above. Otherwise, install Ubuntu using PXE first.

### Inventory and Variables

Follow the group pattern in [inventory/dns/inventory.ini](../inventory/dns/inventory.ini):

{% raw %}
```ini
[baremetal]
new-physical-host

[python]
new-physical-host

[pxe_client]
new-physical-host

[pxe]
pxe-0
```
{% endraw %}

Add unique global IP mappings for the client and PXE server. Define client variables using the intended interface, MAC address, and IP:

{% raw %}
```yaml
vms_os: ubuntu_24_server
python3_version: "3.12"
pxeserver_setup_client_nic: "enp2s0"
pxeserver_setup_dhcp_range: "<client-ip>,<client-ip>,255.255.255.0"
pxeserver_setup_ip_reservations:
  - mac_address: "<client-mac>"
    ip_address: "<client-ip>"
```
{% endraw %}

Replace all placeholders with real values. The installed client's static address comes from `global_ip_address`, not from the DHCP reservation alone; keep them consistent.

The PXE server also needs `vms_os: ubuntu_24_server` in its own resolved variables, because deployment downloads `global_os[vms_os]` artifacts in the server's context. Client and server must select matching installation artifacts. Configure the server's listening interface and HTTP/storage settings for its actual environment. `pxeserver_setup_host` defaults to the first member of `pxe`.

### Installation Sequence and Safety

Back up the physical host before netbooting it. The autoinstall configuration uses an LVM storage layout with all sizing; treat installation as destructive. Confirm the intended installation disk and do not leave valuable disks exposed to an unattended installer.

Configure and install **one client at a time**. Client configuration replaces shared server files, including `user-data`, `meta-data`, `pxelinux.cfg/default`, and dnsmasq configuration; it is not an isolated per-client boot profile. Do not reconfigure the server for another client while an installation is in progress.

{% raw %}
```shell
BAREMETAL_HOST=new-physical-host
ansible-playbook -i "$INV" playbooks/pxe/deploy_pxe.yml
ansible-playbook -i "$INV" playbooks/pxe/configure_pxe.yml --limit "$BAREMETAL_HOST"
```
{% endraw %}

The deploy play targets the PXE server; the configure play targets the client and delegates server configuration. Add authentication/vault options as required. Confirm network boot firmware compatibility with the provided PXELINUX configuration; do not assume all UEFI hosts can use it unchanged. Under TP-Link Omada, allow the PXE server IP in the "Legal DHCP Servers" setting.

Network-boot the physical host and let autoinstall finish. The boot parameters direct it to download the ISO and NoCloud autoinstall data over HTTP from the PXE server. Verify SSH access, disable or deprioritize network boot to avoid accidental reinstall, then set `HOST` to the baremetal hostname and run step 7's staged post-install commands. Review disk preparation separately.

## ✅ 9. Verify Provisioning

For a VM, confirm the requested hostname, destination node, running state, CPU, memory, storage, NIC bridge/VLAN, and boot disk size in Proxmox. Verify actual guest-agent availability, not just the enabled Proxmox option.

For both VM and baremetal hosts:

1. Confirm the OS release, IP address, routes, and DNS match the intended configuration.
2. Check cloud-init completion for cloud-init guests, or autoinstall completion for PXE installations.
3. Confirm SSH and privilege escalation work using the intended management account.
4. Confirm Python is available at the configured interpreter path and the virtual environment exists.
5. Check domain membership with `realm list` and verify the intended domain account can authenticate.
6. Verify standard users and baseline node configuration.
7. If disk preparation was approved and run, inspect filesystems, mountpoints, ownership, and `/etc/fstab` against the intended layout.

Test normal Ansible connectivity using the repository's configured interpreter and connection settings:

{% raw %}
```shell
ansible "$HOST" -i "$INV" -m ansible.builtin.ping
```
{% endraw %}

A successful ping alone does not verify domain membership, storage safety, or application health. If any stage fails, inspect its output and the machine's current state before retrying.

## 🔗 What the Top-Level Playbook Calls

| Stage                                                          | Targets                   | Purpose                                                                                                |
| -------------------------------------------------------------- | ------------------------- | ------------------------------------------------------------------------------------------------------ |
| [VM creation](../playbooks/vms/provision_vm.yml)               | `vms`                     | Pi-hole DNS updates followed by Ansible-native or Terraform-backed clone/cloud-init provisioning.      |
| [Python bootstrap](../playbooks/python/bootstrap_python3.yml)  | `python`                  | Installs Python and prepares a virtual environment.                                                    |
| [Domain join](../playbooks/ad/join_domain.yml)                 | `vms`, `baremetal`, `wsl` | Applies domain configuration and joins Active Directory.                                               |
| [Node preparation](../playbooks/ansible/prep_ansible_node.yml) | `vms`, `baremetal`, `wsl` | Applies the managed-node baseline.                                                                     |
| [User provisioning](../playbooks/vms/add_users.yml)            | `vms`, `baremetal`        | Provisions standard users.                                                                             |
| [Disk preparation](../playbooks/vms/prep_disk.yml)             | `vms`, `baremetal`        | Discovers disks, partitions/formats candidates, and applies mounts; requires explicit operator review. |

## 📋 Minimum Inventory Contract

- **New VM:** Membership in `vms` and `python`, a unique global IP entry, required hardware settings in `vms_config`, and `vms_os` selecting an existing compatible template. Shared defaults may supply Python and optional settings. Operational credentials, DNS, SSH, snippets, and storage prerequisites remain mandatory.
- **Existing baremetal host:** Membership in `baremetal` and `python`, a unique global IP entry, an installed supported OS, working SSH/become access, and resolved domain/user/baseline variables. Do not add it to `vms` merely to enable post-install stages.
- **Baremetal PXE installation:** Add `pxe_client` membership and a reachable `pxe` server; define matching OS selections for server and client, real client NIC/MAC/IP values, and appropriate DHCP configuration. Install the OS before running the post-install stages.

## 📌 Notes

- Commit inventory and IP mapping changes together, but never commit plaintext secrets.
- Limit each provisioning run to the intended host and verify all imported stages' targets.
- Keep backups; provisioning, PXE installation, and disk preparation are not substitutes for a recovery plan.
- Use dedicated maintenance tasks for later hardware or software updates rather than assuming this creation workflow is safe to rerun.
