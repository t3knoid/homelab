# ⚙️ Proxmox Virtual Environment (PVE)

**Proxmox VE** is an open‑source virtualization platform that combines KVM (Kernel‑based Virtual Machine) and LXC (Linux Containers) into a single management interface. It provides clustering, high availability, storage integration, and a powerful web‑based UI—making it ideal for both enterprise and homelab deployments.

---

## 🖥️ Proxmox Cluster

The lab runs a **three‑node Proxmox cluster**, providing redundancy and high availability:

- **pve‑0** → [https://192.168.2.200:8006/](https://192.168.2.200:8006/)  
- **pve‑1** → [https://192.168.2.201:8006/](https://192.168.2.201:8006/)  
- **pve‑2** → [https://192.168.2.202:8006/](https://192.168.2.202:8006/)  

The cluster can be managed from any of these URLs, with quorum maintained across all three nodes.  
Installation follows the official [Proxmox instructions](https://www.proxmox.com/en/proxmox-virtual-environment/get-started).

---

## 🖧 Host Details

Each node uses the same hardware platform: [ACEMAGIC S1 Mini PC](https://www.amazon.com/ACEMAGIC-S1-Screen-Intel-3-4GHz/dp/B0CJV69QSN).  

| Hostname | IP Address   | Memory | OS Drive | Secondary Drive |
|----------|--------------|--------|----------|-----------------|
| pve‑0    | 192.168.2.200 | 16GB   | 512GB    | 512GB           |
| pve‑1    | 192.168.2.201 | 16GB   | 512GB    | 512GB           |
| pve‑2    | 192.168.2.202 | 16GB   | 512GB    | 512GB           |

The secondary drive is a [Western Digital Red SA500 NAS SSD](https://www.amazon.com/dp/B07YFG1N7Q). These SSDs are dedicated to the **Ceph distributed storage cluster**, providing resilient, high‑performance storage for VMs and containers.

---

## 📦 Ceph Storage

[[Ceph]] is tightly integrated with Proxmox and provides the cluster’s primary shared storage backend.

### Why Ceph?
- **High Availability:** VM disks are replicated across nodes, eliminating single points of failure.  
- **Scalability:** Storage pools can grow seamlessly by adding more disks or nodes.  
- **Unified Storage:** Supports block storage (RBD), object storage, and filesystem storage.  
- **Self‑Healing:** Automatically rebalances and recovers data when nodes or drives fail.  

### Lab Setup
- Each Proxmox node contributes its secondary SSD as a Ceph OSD (Object Storage Daemon).  
- Ceph monitors (MONs) run on all three nodes to maintain cluster state.  
- A replicated Ceph pool is used for VM disks, ensuring redundancy (e.g., 3‑way replication).  
- VM disks stored on Ceph can be live‑migrated between nodes without downtime.  

### Storage Flow (Text Diagram)
```
[ VM Disk ] → stored in → [ Ceph Pool ]
                 ↑
   replicated across → [ OSDs on pve-0, pve-1, pve-2 ]
                 ↑
   managed by → [ Ceph MONs on all nodes ]
```

This mirrors enterprise‑grade storage practices while remaining lightweight enough for homelab hardware.

---

## 💡 Proxmox Tips & Hints

### ISO Images
Store ISO images in the following directory on each node:

```bash
/var/lib/vz/template/iso/
```

### CT Templates
Container templates are stored here:

```bash
/var/lib/vz/template/cache/
```

### Handy Notes
- Keep ISOs and templates synchronized across nodes for consistency.  
- Use **Proxmox Backup Server** alongside Ceph for snapshotting and deduplication.  
- Monitor Ceph health with `ceph -s` to ensure replication and recovery are functioning correctly.  

---

## 🚀 Why This Matters

By combining **Proxmox clustering** with **Ceph distributed storage**, the lab achieves:
- High availability for workloads  
- Seamless VM migration across nodes  
- Enterprise‑style storage resiliency  
- Hands‑on experience with production‑grade virtualization and storage technologies  

This makes the homelab not just a sandbox, but a true mirror of modern infrastructure practices.

