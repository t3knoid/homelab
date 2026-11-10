---
title: "TrueNAS"
---

# 💾 TrueNAS

TrueNAS is a network-attached storage platform built around ZFS. Pools provide storage capacity, datasets organize data and its properties, and shares expose selected paths to clients. SMB commonly serves desktop file access, while NFS provides shared filesystem access for Linux hosts and applications. Dataset permissions, identities, and network restrictions determine who can actually access exported data.

ZFS snapshots can support recovery from unwanted changes, but snapshots on the same storage are not independent backups. Redundancy, snapshots, and backups address different failure scenarios and must be planned separately.

TrueNAS provides shared storage for media, application configuration, project files, and backup destinations. Keeping these paths on the NAS lets selected services consume persistent data independently of their application VM, but also makes those consumers dependent on NAS and network availability.

| Item                                  | Repository Configuration                                                      |
| ------------------------------------- | ----------------------------------------------------------------------------- |
| Inventory hostname                    | `truenas-01`                                                                  |
| Address                               | `192.168.2.250`                                                               |
| Management alias                      | `truenas.refol.us`, defined as a CNAME to `rproxy-0.refol.us`                 |
| Pool/dataset prefix in host variables | `Data`                                                                        |
| File-sharing services                 | SMB (`cifs`) and NFS                                                          |
| Other configured services             | SSH and UPS service; UPS hardware/action policy still needs documenting       |
| Ansible connection                    | SSH as `ansible`, with role-controlled root escalation for middleware access  |
| Role version requirement              | TrueNAS 25.10+; this is a minimum requirement, not a verified running version |

Sources: [inventory](https://github.com/t3knoid/ansible/blob/main/inventory/truenas/inventory.ini), [host configuration](https://github.com/t3knoid/ansible/blob/main/inventory/truenas/host_vars/truenas-01/default.yml), and [role defaults](https://github.com/t3knoid/ansible/blob/main/roles/truenas/defaults/main.yml). A configured service or dataset is desired state, not proof that it currently exists or is healthy.

## 📁 Storage and Workloads

| Storage Area                                                                  | Intended Use or Repository Evidence                                                                                                                                                         |
| ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/mnt/Data/movies`, `/mnt/Data/music`, `/mnt/Data/tvshows`, `/mnt/Data/books` | Media/library paths; the [Plex inventory](https://github.com/t3knoid/ansible/blob/main/inventory/plex/group_vars/all/main.yml) declares NAS-backed mounts                                                                             |
| `/mnt/Data/downloads/complete` and related download paths                     | Shared download storage referenced by [Sonarr](https://github.com/t3knoid/ansible/blob/main/inventory/services/group_vars/sonarr/main.yml), [Radarr](https://github.com/t3knoid/ansible/blob/main/inventory/services/group_vars/radarr/main.yml), and other service inventories |
| `Data/configs` and child datasets                                             | Application-specific configuration datasets declared in NAS host variables; complete the consumer/path map before treating it as a dependency inventory                                     |
| `/mnt/Data/ecube/*`                                                           | Project/demo paths declared as SMB/NFS exports                                                                                                                                              |
| `/mnt/Data/backups_ex`                                                        | Backup destination exported over NFS; the [Prometheus inventory](https://github.com/t3knoid/ansible/blob/main/inventory/prometheus/group_vars/all/main.yml) declares a backup mount                                                   |
| Other datasets and exports                                                    | See NAS host variables for photo, incoming, FTP, and other paths; document actual owners and consumers separately                                                                           |

Dataset definitions, share definitions, and client mounts are separate configuration surfaces.

## ⚙️ How Configuration Is Managed

[configure_truenas.yml](https://github.com/t3knoid/ansible/blob/main/playbooks/truenas/configure_truenas.yml) applies the `global` and `truenas` roles to the `truenas` inventory group. Ansible connects to the NAS over SSH and configures it through the TrueNAS middleware API, the same API the web UI uses. It configures an already-installed system. It does not install TrueNAS, set up the boot device, or create the first storage pool.

After its preflight checks, the role runs each enabled stage in order: updates, network interfaces, groups, administrator settings, users, Active Directory, datasets, shares, and services. Each stage has a tag for targeted runs. A tag processes the stage's whole configured list, not just the item you added. Raw post-configuration calls need extra care because they are not idempotent. Apps and virtual machines are managed separately, with `deploy_truenas_apps.yml` and `deploy_truenas_vms.yml`.

Environment-specific settings belong in the inventory host variables, and secrets go in the encrypted vault files.

[truenas_api](truenas_api.md) is the custom Ansible module behind the role. It compares each object on the NAS with the inventory and changes only what differs, so you can review the plan in check mode before applying it.

For hands-on work, `midclt` is the command-line client for the same middleware API. Run it from the TrueNAS shell to inspect live settings or troubleshoot a failed job. See the [midclt Cheat Sheet](midclt_cheat_sheet.md) for common commands.

For variables, tags, API behavior, and safety limits, see the [TrueNAS Role Contributor Guide](truenas_role_contributor_guide.md).

## 📚 Administrator Runbooks

See [Runbooks#-TrueNAS-Management](runbooks#-truenas-management.md) for a list of TrueNAS management runbooks.