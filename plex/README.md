# Plex

## Installation

Plex is installed from the Plex repo using the following sourcelist file:

/etc/apt/sources.list.d/plexmediaserver.list

The file contains the following line:

```bash
deb [arch=amd64 signed-by=/usr/share/keyrings/plexmediaserver.gpg] https://downloads.plex.tv/repo/deb/ public main
```

Use the following command to install or update of the plexmediaserver package:

```bash
sudo apt-get update
sudo apt-get install plexmediaserver
```

## Host Details

Plex is installed in the following host:

- Hostname: xpenology
- IP Address: 192.168.2.220 (Static)
- Operating System: Ubuntu 24.04.1 LTS (Noble Numbat)

## Media Shares with Autofs

Media is shared using NFS autofs mounts. In order to properly mount the shares shared by the Truenas server, the following setting must be enabled in /etc/autofs.conf.

```bash
mount_nfs_default_protocol = 3
```

### /etc/auto.master

Add the following line in /etc/auto.master to set the root nfs mount point.

```bash
/nfs    /etc/auto.nfs
```

### /etc/auto.nfs

The /etc/auto.nfs file contains the necessary NFS mounts from the TrueNAS server.

```bash
movies  192.168.2.250:/mnt/Data/movies
music   192.168.2.250:/mnt/Data/music
tvshows 192.168.2.250:/mnt/Data/tvshows
books   192.168.2.250:/mnt/Data/books
downloads 192.168.2.250:/mnt/Data/downloads/complete
incomplete-downloads 192.168.2.250:/mnt/Data/downloads/incomplete
```

These mounts are automatically mounted in the root nfs folder (i.e., /nfs) using the autofs service. Accessing the specific mount point will dynamically mount the remote NFS file system.

### Starting Autofs

```bash
sudo systemctl restart autofs
sudo systemctl restart rpcbind
```