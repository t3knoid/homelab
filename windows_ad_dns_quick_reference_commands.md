---
title: "Windows AD DNS Quick Reference Commands"
---

# Windows AD DNS Quick Reference Commands

| Area | Action | Command | Description |
|------|--------|---------|-------------|
| **Forward Zones** | Create forward zone | `Add-DnsServerPrimaryZone -Name "refol.us" -ZoneFile "refol.us.dns"` | Creates the primary AD forward zone. |
| | Validate forward zone | `Get-DnsServerZone -Name "refol.us" \| Format-List *` | Shows zone details. |
| **Reverse Zones** | Create reverse zone | `Add-DnsServerPrimaryZone -NetworkId "192.168.20.0/24" -ZoneFile "20.168.192.in-addr.arpa.dns" -ZoneType Primary` | Creates reverse zone for the subnet. |
| | Delete reverse zone | `Remove-DnsServerZone -Name "20.168.192.in-addr.arpa" -Force` | Removes a reverse zone. |
| | List reverse zones | `Get-DnsServerZone \| Where-Object { $_.IsReverseLookupZone }` | Shows all reverse zones. |
| **PTR Records** | List PTRs | `Get-DnsServerResourceRecord -ZoneName "20.168.192.in-addr.arpa" -RRType PTR` | Displays PTR records. |
| | Add PTR | `Add-DnsServerResourceRecordPtr -Name "50" -ZoneName "20.168.192.in-addr.arpa" -PtrDomainName "host.refol.us"` | Adds PTR for `192.168.20.50`. |
| | Remove PTR | `Remove-DnsServerResourceRecord -ZoneName "20.168.192.in-addr.arpa" -RRType PTR -Name "50" -Force` | Removes PTR for `.50`. |
| **Forwarders** | Add forwarder | `Add-DnsServerForwarder -IPAddress "8.8.8.8"` | Adds Google DNS as a forwarder. |
| | Add forwarder | `Add-DnsServerForwarder -IPAddress "1.1.1.1"` | Adds Cloudflare DNS as a forwarder. |
| | Validate forwarders | `Get-DnsServerForwarder` | Lists configured forwarders. |
| | Test forwarding | `Resolve-DnsName google.com -Server 127.0.0.1` | Confirms DNS resolution via the DC. |
| | Test port | `Test-NetConnection -ComputerName 8.8.8.8 -Port 53` | Confirms DNS port connectivity. |
| | Check DNS logs | `Get-WinEvent -LogName "DNS Server" -MaxEvents 50 \| Format-Table TimeCreated, Id, Message -AutoSize` | Shows recent DNS server events. |
| **SRV & A Records** | Validate SRV records | `Get-DnsServerResourceRecord -ZoneName "refol.us" -RRType "SRV"` | Ensures AD service records exist. |
| | Validate DC A record | `Get-DnsServerResourceRecord -ZoneName "refol.us" -Name "dc01"` | Confirms the DC hostname resolves. |
| **Testing** | Forward lookup | `Resolve-DnsName hostname.refol.us` | Tests A‑record resolution. |
| | Reverse lookup | `Resolve-DnsName 192.168.20.50` | Tests PTR resolution. |

---