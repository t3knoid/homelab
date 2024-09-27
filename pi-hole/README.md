# Pi-hole

[Pi-hole](https://pi-hole.net/) is a very simple to use DNS that also provides network-wide ad blocking.

## Installation

Installation is straightforward as documented at https://docs.pi-hole.net/main/basic-install/.

Manually download the installer and execute.

```bash
wget -O basic-install.sh https://install.pi-hole.net
sudo bash basic-install.sh
```

The server is installed on a very minimal VM. 

There are three Pi-Hole instances hosted in the hosts 192.168.2.252, 192.168.2.253, 192.168.2.254.

Note that 192.168.2.254 is not actively used. The to nodes, 192.168.2.252 and 192.168.2.253 are synced using [gravity-sync](https://github.com/vmstan/gravity-sync/wiki/Installing).

## Configuration

### Integration with Active Directory

In order to use Pi-Hole as the primary DNS server with Windows Active Directory (i.e., 192.168.2.251), enable the Use Conditional Forwarding option.

1. Open the Pi-Hole admin page.
2. Navigate to  Settings > DNS.
3. Scroll to the bottom of the page and enable the "Use Conditional Forwarding" checkbox.
4. Enter "192.168.2.0/24" in the Local Network field.
5. Enter "192.168.2.252 in the "IP address of your DHCP server" field.
6. Enter "refol.us" in the "Local domain name" field.
 
## Admin Webpage

The admin webpage is accessible from a browser using the address http://pi.hole/admin or http://192.168.2.252/admin.

Login using the password X6uDOu9B.

## Usage

Open the TP-Link Omada management page at https://omada.tplinkcloud.com/ and perform the following:
1. Open Settings > Wired Networks > LAN.
2. Edit the Default network.
3. Set the DNS Server to Manual.
4. Enter 192.168.2.252, 192.168.2.253, 192.168.2.254.

