# Home Lab

The following document summarizes my home lab.

## Overview

My home lab centers around a [Proxmox](proxmox/README.md) server cluster providing the necessary VMs for hosts used in the lab environment.

To simplify networking, the existing home network will be used instead of creating a separate VLAN. The network is comprised of [TP-Link Omada](omada/README.md) devices.




## Virtualization

Virtual machines will be hosted in [Proxmox](proxmox/README.md). [Linstor](/proxmox/linstor_install.md) will provide high-availability for virtual machine storage.

## Active Directory

The [Microsoft Active Directory](activedirectory/README.md) server is hosted in virtual machine running Windows 2022.

## DNS

DNS is provided using [Pi-Hole DNS](pi-hole/README.md). There are two active Pi-hole servers that are hosted in virtual machines in Proxmox.

## Ansible

[Ansible](ansible/README.md) will be used to automate most of the virtual management and its associated applications.

[Semaphore](semaphore/README.md) will be use as a front-end for running Ansible scripts.

## Jenkins

[Jenkins](jenkins/README.md) will be used as the primary CI/CD frontend.

## Load Balancing

[Nginx](https://docs.nginx.com/nginx/admin-guide/load-balancer/http-load-balancer/) will be used for load-balancing.

## Forward Proxy

[tinyproxy](tinyproxy/README.md)

## Reverse Proxy

[Nginx](nginx/README.md)

## VDI
  - https://github.com/joshpatten/PVE-VDIClient
  - PVE-VDIClient tutorial (https://www.youtube.com/watch?v=oLatrZBFQrw)
  - https://pve.proxmox.com/wiki/SPICE
  - https://www.deskpool.com/
  - https://guacamole.apache.org/

## Single-Sign-On
  - https://www.reddit.com/r/opensource/comments/102k8dt/sso_solution_suggestion/
  - KeyCloak, https://www.keycloak.org/
  - Authentik (https://goauthentik.io/)

## References and Tutorials

- https://github.com/afro-systems/lxc-guac-setup



