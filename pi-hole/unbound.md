# Unbound

[Unbound](https://docs.pi-hole.net/guides/dns/unbound/) is a recursive DNS server. It directly contacts authoritative servers to resolve a DNS query.

## Install Unbound

To install unbound, execute the following from the Pi-hole host console.

```bash
sudo apt update
sudo apt install unbound
```

## Configure Unbound

Unbound will need to be configured to work with the Pi-hole instance that is running locally.

Create a new file /etc/unbound/unbound.conf.d/pi-hole.conf. Use the following content as a starting point.

```yaml
server:
    # If no logfile is specified, syslog is used
    # logfile: "/var/log/unbound/unbound.log"
    verbosity: 0

    interface: 127.0.0.1
    port: 5335
    do-ip4: yes
    do-udp: yes
    do-tcp: yes

    # May be set to yes if you have IPv6 connectivity
    do-ip6: no

    # You want to leave this to no unless you have *native* IPv6. With 6to4 and
    # Terredo tunnels your web browser should favor IPv4 for the same reasons
    prefer-ip6: no

    # Use this only when you downloaded the list of primary root servers!
    # If you use the default dns-root-data package, unbound will find it automatically
    #root-hints: "/var/lib/unbound/root.hints"

    # Trust glue only if it is within the server's authority
    harden-glue: yes

    # Require DNSSEC data for trust-anchored zones, if such data is absent, the zone becomes BOGUS
    harden-dnssec-stripped: yes

    # Don't use Capitalization randomization as it known to cause DNSSEC issues sometimes
    # see https://discourse.pi-hole.net/t/unbound-stubby-or-dnscrypt-proxy/9378 for further details
    use-caps-for-id: no

    # Reduce EDNS reassembly buffer size.
    # IP fragmentation is unreliable on the Internet today, and can cause
    # transmission failures when large DNS messages are sent via UDP. Even
    # when fragmentation does work, it may not be secure; it is theoretically
    # possible to spoof parts of a fragmented DNS message, without easy
    # detection at the receiving end. Recently, there was an excellent study
    # >>> Defragmenting DNS - Determining the optimal maximum UDP response size for DNS <<<
    # by Axel Koolhaas, and Tjeerd Slokker (https://indico.dns-oarc.net/event/36/contributions/776/)
    # in collaboration with NLnet Labs explored DNS using real world data from the
    # the RIPE Atlas probes and the researchers suggested different values for
    # IPv4 and IPv6 and in different scenarios. They advise that servers should
    # be configured to limit DNS messages sent over UDP to a size that will not
    # trigger fragmentation on typical network links. DNS servers can switch
    # from UDP to TCP when a DNS response is too big to fit in this limited
    # buffer size. This value has also been suggested in DNS Flag Day 2020.
    edns-buffer-size: 1232

    # Perform prefetching of close to expired message cache entries
    # This only applies to domains that have been frequently queried
    prefetch: yes

    # One thread should be sufficient, can be increased on beefy machines. In reality for most users running on small networks or on a single machine, it should be unnecessary to seek performance enhancement by increasing num-threads above 1.
    num-threads: 1

    # Ensure kernel buffer is large enough to not lose messages in traffic spikes
    so-rcvbuf: 1m

    # Ensure privacy of local IP ranges
    private-address: 192.168.0.0/16
    private-address: 169.254.0.0/16
    private-address: 172.16.0.0/12
    private-address: 10.0.0.0/8
    private-address: fd00::/8
    private-address: fe80::/10
```

Create the file /etc/dnsmasq.d/99-edns.conf and add the following line to signal FTL to adhere to this limit.:

```ini
edns-packet-max=1232
```

## Start Unbound

Restart the unbound service.

```bash
sudo service unbound restart
```

Validate that the service is working.

```bash
dig pi-hole.net @127.0.0.1 -p 5335
```

```bash
; <<>> DiG 9.18.28-0ubuntu0.24.04.1-Ubuntu <<>> pi-hole.net @127.0.0.1 -p 5335
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 29561
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 1232
;; QUESTION SECTION:
;pi-hole.net.                   IN      A

;; ANSWER SECTION:
pi-hole.net.            300     IN      A       3.18.136.52

;; Query time: 89 msec
;; SERVER: 127.0.0.1#5335(127.0.0.1) (UDP)
;; WHEN: Wed Oct 02 13:22:21 UTC 2024
;; MSG SIZE  rcvd: 56
```

## Test validation

The following command should give a status report of SERVFAIL and no IP address.

```bash
dig fail01.dnssec.works @127.0.0.1 -p 5335
```

The following should give NOERROR plus an IP address.
```bash
dig dnssec.works @127.0.0.1 -p 5335
```

## Configure Pi-hole

Open the Pi-hole web interface and navigate to Settings > DNS. Add the following as a custom **Upstream DNS Servers**

```bash
127.0.0.1#5335
```

Uncheck all other upstream DNS settings.

## References

- https://docs.pi-hole.net/guides/dns/unbound/