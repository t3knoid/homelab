# iSCSI 

iSCSI (Internet Small Computer System Interface) is a protocol that allows SCSI commands to be transmitted over TCP/IP networks. It enables the creation of Storage Area Networks (SANs) using existing network infrastructure.

## Key Components

iSCSI Initiator: The client-side component that initiates the connection to the iSCSI target.

iSCSI Target: The server-side component that provides storage resources.

## How It Works
Initiation: The iSCSI initiator sends SCSI commands encapsulated in IP packets to the iSCSI target.

Transmission: The iSCSI target receives the IP packets, extracts the SCSI commands, and processes them.

Data Transfer: Data is transferred between the initiator and target as if it were a local storage device, even though it's over a network.

## Helpful iSCSI Related Commands

The following are commands that are related to managing iSCSI.

### List Active Sessions

Use the list session command to show active iscsi connections.

```bash
iscsiadm -m session
```

### Logout of a Session

```bash
iscsiadm -m node --logout -T IQN
```

Substitute **IQN** shown above with actual IQN identifier.

### Delete a Target

Make sure to logout of the session connected to the target to be deleted.

```bash
iscsiadm -m node -o delete -T IQN
```

Substitute **IQN** shown above with actual IQN identifier.

### Disable iSCSI services

```bash
sudo systemctl enable open-iscsi
sudo systemctl enable iscsid
```

### Troubleshooting


#### Initiator Reported Error (15 - session exists)

If the following error is thrown while trying to perform a backup using the iscsi device,

> iscsiadm: Could not login to [iface: default, target: iqn. 2000-01.com.synology:synology-0.Target-1.76fd697e949, portal: fe80::211:32ff:fe8a:51d9,3260].
iscsiadm: initiator reported error (15 - session exists)
iscsiadm: Could not log into all portals

Connect to the PVE host that is having this issue and perfom the following command as root:

```bash
iscsiadm -m node --logoutall=all
```

This typically happens if the Synology server that is hosting the iscsi block device boots after the PVE servers.

