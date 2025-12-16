# Linstor Management

The following page provides some insight on managing Linstor.

## Changing IP Address of Clusters

### Stop the following services.

``` shell
systemctl stop pve-cluster
systemctl stop corosync
systemctl stop linstor-controller.service
systemctl stop linstor-satellite.service
```

### Modify Node IP addresses in /etc/corosync/corosync.conf

``` shell
vi /etc/corosync/corosync.conf

```

Change IP Addresses of each node.

### Modify Controller IP in /etc/pve/storage.cfg

``` shell
vi /etc/pve/storage.cfg

```

Change IP to controller IP

### Start Services
``` shell

killall pmxcfs
systemctl start corosync
systemctl start pve-cluster
systemctl start linstor-controller.service
systemctl start linstor-satellite.service

```

## Modify Node IP Address

``` shell
linstor node interface modify --ip 192.168.2.200 pve-0 default
linstor node interface modify --ip 192.168.2.201 pve-1 default
linstor node interface modify --ip 192.168.2.202 pve-2 default
```

## Verify Node Cluster

``` shell
linstor node list
```
An output should display something like the following.
``` shell
╭────────────────────────────────────────────────────────╮
┊ Node  ┊ NodeType ┊ Addresses                  ┊ State  ┊
╞════════════════════════════════════════════════════════╡
┊ pve-0 ┊ COMBINED ┊ 192.168.2.200:3366 (PLAIN) ┊ Online ┊
┊ pve-1 ┊ COMBINED ┊ 192.168.2.201:3366 (PLAIN) ┊ Online ┊
┊ pve-2 ┊ COMBINED ┊ 192.168.2.202:3366 (PLAIN) ┊ Online ┊
╰────────────────────────────────────────────────────────╯
```

When a node is EVICTED, as shown here, this usually means that the node was down and could not be joined with the cluster.
```shell
╭─────────────────────────────────────────────────────────╮
┊ Node  ┊ NodeType ┊ Addresses                  ┊ State   ┊
╞═════════════════════════════════════════════════════════╡
┊ pve-0 ┊ COMBINED ┊ 192.168.2.200:3366 (PLAIN) ┊ Online  ┊
┊ pve-1 ┊ COMBINED ┊ 192.168.2.201:3366 (PLAIN) ┊ EVICTED ┊
┊ pve-2 ┊ COMBINED ┊ 192.168.2.202:3366 (PLAIN) ┊ Online  ┊
╰─────────────────────────────────────────────────────────╯
```
Restore the node by running the "node restore" command. Here's an example of the command to bring back pve-1 back online.

```sudo linstor node restore pve-1```

## List Resources

Use the following command to list resources.

``` shell
linstor resource list
```

This command shows something like the following.

``` shell
╭───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
┊ ResourceName ┊ Node  ┊ Port ┊ Usage  ┊ Conns                   ┊              State ┊ CreatedOn           ┊
╞═══════════════════════════════════════════════════════════════════════════════════════════════════════════╡
┊ pm-0c0e1528  ┊ pve-0 ┊ 7011 ┊ Unused ┊ Ok                      ┊           UpToDate ┊ 2024-09-18 10:37:42 ┊
┊ pm-0c0e1528  ┊ pve-1 ┊ 7011 ┊ Unused ┊ Ok                      ┊           UpToDate ┊ 2024-09-18 10:37:47 ┊
┊ pm-0c0e1528  ┊ pve-2 ┊ 7011 ┊ InUse  ┊ Ok                      ┊           UpToDate ┊ 2024-09-18 10:37:47 ┊
```

If a resource shows a property of *SkipDisk* as shown here,

``` shell
┊ pm-0c0e1528  ┊ pve-2 ┊ 7011 ┊ InUse  ┊ Ok    ┊ Diskless, SkipDisk (R) ┊ 2024-09-18 10:37:47 ┊
```

This indicates an IO error on the affected resource(s). Remove this property (using 'linstor resource set-property $node $rsc DrbdOptions/SkipDisk') to instruct LINSTOR and DRBD to adjust (and recreate if necessary) the affected logical volumes again. For more information please visit: https://linbit.com/drbd-user-guide/linstor-guide-1_0-en/#s-linstor-drbd-skip-disk

Use the following one-liner to find all affected resource and remove this property.

``` shell
linstor resource list | grep "SkipDisk (R)" | awk -F'|' '{print $2 $3}' | xargs -I{} bash -c 'set -- {}; linstor resource set-property $2 $1 DrbdOptions/SkipDisk'
```