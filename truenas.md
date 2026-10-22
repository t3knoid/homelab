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
| `/mnt/Data/movies`, `/mnt/Data/music`, `/mnt/Data/tvshows`, `/mnt/Data/books` | Media/library paths; the [Plex inventory](../inventory/plex/group_vars/all/main.yml) declares NAS-backed mounts                                                                             |
| `/mnt/Data/downloads/complete` and related download paths                     | Shared download storage referenced by [Sonarr](../inventory/services/group_vars/sonarr/main.yml), [Radarr](../inventory/services/group_vars/radarr/main.yml), and other service inventories |
| `Data/configs` and child datasets                                             | Application-specific configuration datasets declared in NAS host variables; complete the consumer/path map before treating it as a dependency inventory                                     |
| `/mnt/Data/ecube/*`                                                           | Project/demo paths declared as SMB/NFS exports                                                                                                                                              |
| `/mnt/Data/backups_ex`                                                        | Backup destination exported over NFS; the [Prometheus inventory](../inventory/prometheus/group_vars/all/main.yml) declares a backup mount                                                   |
| Other datasets and exports                                                    | See NAS host variables for photo, incoming, FTP, and other paths; document actual owners and consumers separately                                                                           |

Dataset definitions, share definitions, and client mounts are separate configuration surfaces.

## ⚙️ How Configuration Is Managed

[configure_truenas.yml](https://github.com/t3knoid/ansible/blob/main/playbooks/truenas/configure_truenas.yml) applies the `global` and `truenas` roles to the `truenas` inventory group. It configures an already-installed appliance through local middleware over SSH; it does not install TrueNAS, provision the boot device, or create the initial storage pool.

The role performs preflight checks, then enabled stages for updates, groups, administrator settings, users, network/AD, datasets, shares/resources, and services. Most stages have tags for targeted work. A selected tag usually processes the complete configured list, not just one new object; raw post-configuration calls require particular care because they are not generally idempotent.

The [TrueNAS Role Contributor Guide](truenas_role_contributor_guide.md) explains variables, tags, API behavior, and safety limits. Environment-specific changes belong in inventory host variables, with secrets in encrypted vault files. 

## 📚 Administrator Runbooks

| Task                                | Runbook                                                                      | Status                                                     |
| ----------------------------------- | ---------------------------------------------------------------------------- | ---------------------------------------------------------- |
| Add local accounts/groups           | [Add Local Users](runbooks/truenas_add_users.md)                             | Written procedure; validate against the target environment |
| Add SMB/NFS exports                 | [Add Shares](runbooks/truenas_add_shares.md)                                 | Written procedure; validate permissions and clients        |
| Prepare SSH and automation access   | [Bootstrap for Ansible](runbooks/truenas_bootstrap_ansible.md)               | Scaffold                                                   |
| Design or change access permissions | [Dataset Permissions and ACLs](runbooks/truenas_manage_permissions.md)       | Scaffold                                                   |
| Rename or retire exports            | [Modify or Retire Shares](runbooks/truenas_modify_retire_shares.md)          | Scaffold                                                   |
| Change credentials and memberships  | [Manage Users and Credentials](runbooks/truenas_manage_users_credentials.md) | Scaffold                                                   |
| Configure domain integration        | [Active Directory](runbooks/truenas_active_directory.md)                     | Scaffold                                                   |
| Manage dataset properties           | [Create and Modify Datasets](runbooks/truenas_manage_datasets.md)            | Scaffold                                                   |
| Plan an upgrade                     | [Update TrueNAS Safely](runbooks/truenas_update_safely.md)                   | Scaffold                                                   |
| Diagnose failed configuration runs  | [Troubleshoot Configuration](runbooks/truenas_troubleshoot_configuration.md) | Scaffold                                                   |

