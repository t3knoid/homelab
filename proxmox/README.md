# Proxmox

Proxmox provides hosting for Virtual Machines.

- [Proxmox Cluster](#proxmox-cluster)
- [Host Details](#host-details)
- [Proxmox Hints](#proxmox-hints)
  - [ISO Images](#iso-images)
  - [CT Templates](#ct-templates)

## Proxmox Cluster
Proxmox is configured as a three-node cluster with the following nodes:

- pve-0 (https://192.168.2.200:8006/)
- pve-1 (https://192.168.2.201:8006/)
- pve-2 (https://192.168.2.202:8006/)

The cluster can be manage from any of the URL listed above.

## Host Details

Each host uses the same mini PC platform, [ACEMAGIC S1 Mini PC](https://www.amazon.com/ACEMAGIC-S1-Screen-Intel-3-4GHz/dp/B0CJV69QSN/ref=sr_1_3_pp?crid=2E8DG0SFO2WIB&dib=eyJ2IjoiMSJ9.vkZooebXgYqXDEdUuo04T_CnedHOGdsWW5qUiD85xCGuypshjjEZGQTKUTDbNvQw-Tq7ScnvoJA855_b94yb1jBXXK-bbU32R-5TEOZrn1VKivyXSk2APzQ-5QfRBc-eq46lS23iqVwPFUAHFT9BGw.auvd-kwE4oUOmTwewMkPkfdmqiRG6XM1gv7cLigI1o4&dib_tag=se&keywords=acemagic+s1&qid=1726178408&sprefix=acemagic+s1%2Caps%2C107&sr=8-3). 
| Hostname | IP Address | Memory | OS Drive | Secondary Drive |
|----------|------------|------------|------------|------------|
| pve-0 | 192.168.2.200 | 16MB | 512GB | 512GB |
| pve-1 | 192.168.2.201 | 16MB | 512GB | 512GB |
| pve-2 | 192.168.2.202 | 16MB | 512GB | 512GB |

The secondary drive is a [Western Digital Red SA500 NAS SSD SATA III drive](https://www.amazon.com/dp/B07YFG1N7Q?ref=ppx_yo2ov_dt_b_fed_asin_title). This drive is used to provide [DRBD](https://linbit.com/drbd/) (Distributed Replicated Block Device) type storage used in the Linstor configuration.

## Proxmox Hints

### ISO Images

ISO Images are located in the following folder of a respective Proxmox node.

```bash
/var/lib/vz/template/iso/
```

### CT Templates

CT Templates are located in the following folder of a respective Proxmox node.
```bash
 /var/lib/vz/template/cache/
 ```