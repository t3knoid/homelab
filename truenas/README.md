# TrueNas

## Host Details

- AsRock Motherboard with IPMI.
- Product:To Be Filled By O.E.M.
- Model:Intel(R) Atom(TM) CPU C2550 @ 2.40GHz
- Memory:31 GiB
- System Serial:To Be Filled By O.E.M.

## TrueNas Details

Version: Dragonfish-24.04.2.1

## Networking

There are three network cards. One is reserved for IPMI.

| Name | Mac Address | IP Address | Switch Port |
|------|-------------|------------|------------|
| IPMI | D0:50:99:E2:FA:25 | 192.168.2.5 | 1 |
| enp7s0 | D0:50:99:D1:DC:20 | 192.168.2.250 | 3 |
| enp8s0 | D0:50:99:D1:DC:21 | Not used | 5 |

## Storage

### Disks

| Name | Serial | Disk Size | Pool |
|------|------|------|------|
| sda | ZR151742 | 7.28 TiB | Data |
| sdb | ZR14WAKV | 7.28 TiB | Data |
| sdc | ZR1516YM | 7.28 TiB | Data |
| sdd | ZR14VLNP | 7.28 TiB | Data |
| sde | 4C532000000605117325 | 7.28 TiB | Data |
| sdf | 4C532 | 29.82 GiB | boot-pool |

### Datasets

The following datasets are rooted under the Data/ dataset.

| Dataset Name | NFS | SMB |
|--------------|-----|-----|
| books        | Y | N |
| configs      | Y | N |
| downloads    | Y | N |
| ftp          | Y | N |
| ix-applications | Y | N |
| movies | Y | N |
| music | Y | N |
| onedrive | Y | N |
| public | Y | N |
| users | Y | N |



