---
title: "Runbooks"
---

## 📘 Runbooks

### 🌐 DNS & Networking

| Runbook                                          | Description                                                                                                              |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------ |
| **[Ansible Pi-hole and DNS Management Runbook](ansible_pi-hole_and_dns_management_runbook.md)** | Central reference for all Ansible playbooks managing Pi-hole and DNS, including installation, updates, and host records. |
| **[Update Pi-hole DNS Servers Runbook](update_pi-hole_dns_servers_runbook.md)**       | Step-by-step instructions to deploy or update Pi-hole DNS servers.                                                       |
| **[Request Web Certificates Runbook](request_web_certificates_runbook.md)**         | Step-by-step instructions to request and manage TLS certificates for all hosted websites in the homelab.                 |
| **[Request Web Certificates for a Specific Domain Runbook](request_web_certificates_for_a_specific_domain_runbook.md)**         | Step-by-step instructions to request and manage TLS certificates for a specific website.           |
| **[Join an Ubuntu 24 Host to Active Directory Runbook](join_an_ubuntu_24_host_to_active_directory_runbook.md)** | Step-by-step instructions of joining an Ubuntu 24.04 host to the refol.us Active Directory domain.          |
| **[Configure An Inventory For Entra ID OAuth2](configure_an_inventory_for_entra_id_oauth2.md)** | Step-by-step instructions on how to update an inventory so a site behind rproxy uses oauth2-proxy with Microsoft Entra ID. |
| **[Rotate Azure Entra ID OAuth2 Client Secret Runbook](rotate_azure_entra_id_oauth2_client_secret_runbook.md)** | Follow these steps when Azure Entra ID App Registration secret expires. |

---

### 🎬 Media Services

| Runbook                                  | Description                                                      |
| ---------------------------------------- | ---------------------------------------------------------------- |
| **[Deploy Plex Media Server Runbook](deploy_plex_media_server_runbook.md)** | Step-by-step instructions to deploy or update Plex Media Server. |
| **[Deploy Lidarr Runbook](deploy_lidarr_runbook.md)**            | Step-by-step instructions to deploy or update Lidarr.            |
| **[Deploy Radarr Runbook](deploy_radarr_runbook.md)**            | Step-by-step instructions to deploy or update Radarr.            |
| **[Deploy Sonarr Runbook](deploy_sonarr_runbook.md)**            | Step-by-step instructions to deploy or update Sonarr.            |
| **[Deploy Lazy Librarian Runbook](deploy_lazy_librarian_runbook.md)**    | Step-by-step instructions to deploy or update Lazy Librarian.    |
| **[Deploy Calibre-web Runbook](deploy_calibre-web_runbook.md)**       | Step-by-step instructions to deploy or update Calibre-web.       |
| **[Deploy Sabnzbd Runbook](deploy_sabnzbd_runbook.md)**           | Step-by-step instructions to deploy or update Sabnzbd.           |

---

### 💻 Development & Productivity

| Runbook                            | Description                                                |
| ---------------------------------- | ---------------------------------------------------------- |
| **[Deploy Code Server Runbook](deploy_code_server_runbook.md)** | Step-by-step instructions to deploy or update Code Server. |
| **[Disable Code Server Runbook](disable_code_server_runbook.md)** | Step-by-step instructions to disable Code Server. |
| **[Enable Code Server Runbook](enable_code_server_runbook.md)** | Step-by-step instructions to enable Code Server. |
| **[Deploy SemaphoreUI Runbook](deploy_semaphoreui_runbook.md)** | Instructions to deploy or update SemaphoreUI services.     |
| **[Mirror wiki pages to HTML static page runbook](mirror_wiki_pages_to_html_static_page_runbook.md)** | Step-by-step instructions on mirroring homelab wiki pages to https://homelab.refol.us |
| **[Configure Semaphore UI Projects Runbook](configure_semaphore_ui_projects_runbook.md)** | Instructions on adding or modifying a Semaphore UI project |
| **[Defining When Semaphore Runs a Scheduled Task](defining_when_semaphore_runs_a_scheduled_task.md)** | Provides details on configuring the **cron** field in a Semaphore UI scheduled task |
| **[Configure WSL2 as an Ansible Control Node Runbook](configure_wsl2_as_an_ansible_control_node_runbook.md)** | Step-by-step instructions on how to use WSL2 as an Ansible control node |

---

###  📈 Monitoring & Observability

| Runbook           | Description                |
| ----------------- | -------------------------- |
| **[Adding a Grafana Dashboard](adding_a_grafana_dashboard.md)** | Step-by-step instructions to add, provision, and deploy a new Grafana dashboard through Ansible. |
| **[Adding NGINX Exporter to an Inventory](adding_nginx_exporter_to_an_inventory.md)** | Step-by-step instructions on adding Prometheus NGINX Exporter to an inventory. |
| **[Adding Node Exporter to an Inventory](adding_node_exporter_to_an_inventory.md)** | Step-by-step instructions on adding Prometheus Node Exporter to an inventory. |
| **[Adding Blackbox Exporter Targets](adding_blackbox_exporter_targets.md)** | Step-by-step instructions on adding web probe targets for the Prometheus Blackbox Exporter. |
| **[Adding Postgres Exporter to an Inventory](adding_postgres_exporter_to_an_inventory.md)** | Step-by-Step instructions on adding Prometheus Postgres Exporter to an inventory. |
| **[Deploy nginx-prometheus-exporter to Reverse Proxy hosts](deploy_nginx-prometheus-exporter_to_reverse_proxy_hosts.md)** | Step-by-Step instructions on deploying nginx-prometheus-exporter to the reverse proxy hosts. |
| **[Deploy Blackbox Exporter to Prometheus host](deploy_blackbox_exporter_to_prometheus_host.md)** | Step-by-Step instructions on deploying blackbox-exporter to the Prometheus host. |
| **[Deploy Node Exporter to a Specific Inventory Target](deploy_node_exporter_to_a_specific_inventory_target.md)** | Step-by-Step instructions on deploying node exporter to a specific inventory. |
| **[Deploy PostgreSQL Exporter to the PostgreSQL Inventory](deploy_postgresql_exporter_to_the_postgresql_inventory.md)** | Step-by-Step instructions on deploying postgresql exporter to PostgreSQL inventories. |
| **[Deploy PVE Exporter to Proxmox Nodes](deploy_pve_exporter_to_proxmox_nodes.md)** | Step-by-Step instructions on deploying PVE exporter to Proxmox inventories. |
| **[Deploy Grafana Dashboards](deploy_grafana_dashboards.md)** | Use an Ansible playbook to update provisioned dashboard files on an existing Grafana installation. |

---

### 🖥️ Virtual Machine & System Maintenance

| Runbook           | Description                |
| ----------------- | -------------------------- |
| **[Proxmox VM Template Runbook](proxmox_vm_template_runbook.md)** | Step-by-step instructions to create a cloud-init VM template. |
| **[Virtual Machine Snapshot Runbook](virtual_machine_snapshot_runbook.md)**      | Instructions to create and manage snapshots of virtual machines in the home lab. |
| **[Ubuntu Virtual Machine Disk Expansion Runbook](ubuntu_virtual_machine_disk_expansion_runbook.md)**       | Instructions to expand disk size for Ubuntu virtual machines.                    |
| **[Deploy Linux Security Updates Runbook](deploy_linux_security_updates_runbook.md)** | Instructions to apply security updates to Linux hosts in the home lab.           |
| **[Proxmox Cluster Update Runbook](proxmox_cluster_update_runbook.md)**        | Step‑by‑step instructions to safely update a three‑node Proxmox cluster.         |
| **[Provision a Virtual Machine Runbook](provision_a_virtual_machine_runbook.md)**   | Use an Ansible playbook to deploy a new virtual machine.                         |
| **[NFS Mount Troubleshooting Runbook](nfs_mount_troubleshooting_runbook.md)**     | Troubleshoot NFS issues (autofs and fstab).                                        | 
| **[Web Service Outage Troubleshooting Runbook](web_service_outage_troubleshooting_runbook.md)** | Troubleshoot a web service outage. |
| **[Ubuntu LTS Release Upgrade Runbook](ubuntu_lts_release_upgrade_runbook.md)** | Step-by-step instructions to upgrade Ubuntu from one LTS upgrade to another. Currently configured to upgrade Ubuntu 24.04 LTS VM to Ubuntu 26.04 LTS|
| **[Migrate PostgreSQL 14 to PostgreSQL 18](migrate_postgresql_14_to_postgresql_18.md)** | Manual migration of PostgreSQL 14 to 18. |
| **[Migrate PostgreSQL 17 to PostgreSQL 18](migrate_postgresql_17_to_postgresql_18.md)** | Manual migration of PostgreSQL 17 to 18. |
| **[Migrate a PostgreSQL Instance Between Hosts](migrate_a_postgresql_instance_between_hosts.md)** | Migrate a PostgreSQL instance's logical databases and approved roles from one host to another. |
| **[Decommission a Virtual Machine](decommission_a_virtual_machine.md)** | Instructions on how to properly decommission a virtual machine. |
---

### 💾 TrueNAS Management
| Runbook           | Description                |
| ----------------- | -------------------------- |
| **[Join or Reconfigure TrueNAS Active Directory](join_or_reconfigure_truenas_active_directory.md)** | Manage TrueNAS network configuration and AD integration. |
| **[Add TrueNAS Shares](add_truenas_shares.md)** | Create TrueNAS datasets and SMB or NFS shares. |
| **[Add TrueNAS Local Users](add_truenas_local_users.md)** | Add TrueNAS local users and groups. | 
| **[Bootstrap TrueNAS for Ansible](bootstrap_truenas_for_ansible.md)** | Prepare TrueNAS to use with Ansible. |
| **[Manage TrueNAS Applications](manage_truenas_applications.md)** | Manage TrueNAS applications. |
| **[Create and Modify TrueNAS Datasets](create_and_modify_truenas_datasets.md)** | Manage TrueNAS filesystem datasets. |
| **[Manage TrueNAS Dataset Permissions and ACLs](manage_truenas_dataset_permissions_and_acls.md)** | Define ownership, POSIX permissions, SMB ACLs, and multiprotocol access for TrueNAS datasets. | 
| **[Manage TrueNAS Users and Credentials](manage_truenas_users_and_credentials.md)** | Maintain existing TrueNAS local accounts, supplementary memberships, and credentials. | 
| **[Modify or Retire TrueNAS Shares](modify_or_retire_truenas_shares.md)** | Change or retire TrueNAS SMB/NFS exports. |
| **[Troubleshoot TrueNAS Configuration Runs](troubleshoot_truenas_configuration_runs.md)** | Diagnose TrueNAS configuration failures. | 
| **[Update TrueNAS Safely](update_truenas_safely.md)** | Install an approved TrueNAS release, optionally reboot, and verify service health. |

### 📄 Templates & Miscellaneous

| Runbook                          | Description                                                      |
| -------------------------------- | ---------------------------------------------------------------- |
| **[Runbook Ansible Template](runbook_ansible_template.md)** | Template for creating new Ansible runbooks in the home lab wiki. |