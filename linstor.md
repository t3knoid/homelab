---
title: "Linstor"
---

# Linstor

**************************** No Longer Used ****************************
Linstor provides support of failover of VMs. It uses DRBD to provide persistent storage between the Proxmox node clusters. The storage identified with the "linstor_storage" id has been created to be used by virtual machines or containers. 

Each Proxmox node has a secondary 500Gb SSD that that will be used to create the Linstor storage pools. The [Linstor Setup Guide](linstor_setup_guide.md) provides detailed steps on setting up a Linstor storage. 

