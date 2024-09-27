# Home Lab

The following document summarizes my home lab.

## Overview

My home lab centers around a [Proxmox](proxmox/README.md) server cluster providing the necessary VMs for hosts used in the lab environment.

To simplify networking, the existing home network will be used instead of creating a separate VLAN. The network is comprised of [TP-Link Omada](omada/README.md) devices.

The lab consists of the following services:

- [Microsoft Active Directory](activedirectory/README.md)
- [Pi-Hole DNS](pi-hole/README.md)
- [Jenkins](jenkins/README.md)
- [Ansible](ansible/README.md)

## Load Balancing
  - https://docs.nginx.com/nginx/admin-guide/load-balancer/http-load-balancer/

## Active Directory
  - refol.us domain


## Forward Proxy
  - tinyproxy
  -    
## Nginx

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

## Ansible


## DNS

Pi-Hole will be used as the primary DNS server. There are three DNS servers configured:

- dns-0 (192.168.2.252)
- dns-1 (192.168.2.253)
- dns-2 (192.168.2.254)

## References and Tutorials

- https://github.com/afro-systems/lxc-guac-setup
- 

## LINSTOR Cluster
  - multiple nodes
  - shared storage
    - https://linbit.com/drbd-user-guide/linstor-guide-1_0-en/#s-proxmox-installing-from-linbit-public-repos
    - https://linbit.com/blog/linstor-setup-proxmox-ve-volumes/

