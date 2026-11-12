---
title: "️ Pi-hole Exporter"
---

# 🛡️ Pi-hole Exporter

## 🎯 Purpose

`pihole_exporter` exposes Pi-hole DNS and ad-blocking metrics for Prometheus and Grafana. In this environment, it provides:

* Query volume, block rate, and cache usage for each Pi-hole DNS server
* Blocking status and blocklist (gravity) size
* Top queried domains, top blocked domains, and top clients
* Upstream resolver usage and response times for the local Unbound resolver
* A DNS view alongside the host-level metrics from Node Exporter on the same servers

---

## ⚙️ How It Works

* `pihole_exporter` ([eko/pihole-exporter](https://github.com/eko/pihole-exporter)) runs on each Pi-hole host (`dns-0` and `dns-1`) and listens on port `9617`
* Each exporter reads its local Pi-hole v6 API at `http://127.0.0.1:80`, so each host reports its own counters
* The exporter logs in with the Pi-hole password, reuses the API session, and renews it only when Pi-hole rejects it
* Prometheus scrapes `/metrics` every 30 seconds with a 15 second timeout
* Grafana uses the resulting metrics for Pi-hole dashboards

---

## 🧩 Key Concepts

### 📊 Summary Metrics

These gauges cover the rolling last 24 hours, the same numbers shown on the Pi-hole web dashboard:

* `pihole_status` — `1` when blocking is enabled, `0` when disabled
* `pihole_domains_being_blocked` — number of domains in the gravity blocklist
* `pihole_dns_queries_today` and `pihole_dns_queries_all_types` — total DNS queries
* `pihole_ads_blocked_today` and `pihole_ads_percentage_today` — blocked queries, as a count and a percentage
* `pihole_queries_forwarded` and `pihole_queries_cached` — queries answered upstream or from cache
* `pihole_unique_domains` — distinct domains queried
* `pihole_unique_clients` and `pihole_clients_ever_seen` — client counts
* `pihole_request_rate` — current requests per second

### 🔎 Breakdown Metrics

* `pihole_querytypes` — queries by record type (`type` label: A, AAAA, HTTPS, PTR, and so on)
* `pihole_reply` — replies by type (`type` label: NODATA, NXDOMAIN, CNAME, IP, and so on)
* `pihole_top_queries` and `pihole_top_ads` — most queried and most blocked domains (`domain` label)
* `pihole_top_sources` and `pihole_top_sources_blocked` — busiest clients and clients with the most blocked queries (`source` and `source_name` labels)
* `pihole_forward_destinations` — queries per upstream (`destination` and `destination_name` labels)
* `pihole_forward_destinations_responsetime` and `pihole_forward_destinations_responsevariance` — upstream response time

Pi-hole forwards to the local Unbound resolver (`127.0.0.1#5335`), so that is the main upstream destination. The forward destination metrics also include Pi-hole's own `cache` and `blocklist` entries.

### 🏷️ Labels

Every metric carries a `hostname` label with the address the exporter used to reach Pi-hole. Because each exporter reads its local API, this is `127.0.0.1` on both hosts. Use the Prometheus `instance` label (`dns-0` or `dns-1`) to tell the servers apart.

The top lists are snapshots. Entries that drop out of a top list stop being exported, so these series come and go over time.

---

## 📁 Configuration & Service

**Binary:**
`/usr/local/bin/pihole_exporter`, a link to the versioned binary in `/opt/pihole_exporter`

**Password file:**
`/etc/pihole_exporter/password` (`root:pihole-exporter`, mode `0640`)

**Service:**
`pihole_exporter` (systemd)

**Listener:**
`0.0.0.0:9617`

The service runs as the `pihole-exporter` system user. All settings are passed as command-line flags in the systemd unit. The password is read from the password file through `-pihole_password_file`, so it never appears in the unit file or the process list.

**Role settings** (`roles/pihole_exporter_setup/defaults/main/main.yml`):

* `pihole_exporter_setup_version: "1.3.0"`
* `pihole_exporter_setup_port: 9617`
* `pihole_exporter_setup_pihole_hostname: "127.0.0.1"`
* `pihole_exporter_setup_pihole_port: 80`
* `pihole_exporter_setup_password` — defaults to the `pihole` role's vaulted `pihole_password`

**Prometheus settings** (`roles/prometheus_setup/defaults/main/main.yml`):

* `prometheus_setup_pihole_exporter_job_name: "pihole_exporter"`
* `prometheus_setup_pihole_exporter_port: 9617`
* `prometheus_setup_pihole_alerts_enabled: true`

The password is supplied through Ansible vault; do not put it in this page, metric labels, or other public configuration.

---

## 🚀 Deployment

The `pihole_exporter` inventory group in `inventory/dns/inventory.ini` contains the Pi-hole hosts. Deploy the exporter with:

{% raw %}
```bash
source /opt/python_3.12/bin/activate
ansible-playbook -i inventory/dns/inventory.ini playbooks/prometheus/deploy_pihole_exporter.yml
```
{% endraw %}

The playbook loads `roles/pihole/defaults/main/vault.yml` so the exporter uses the same vaulted `pihole_password` as the `pihole` role. To use a Pi-hole application password instead (**Settings → Web interface / API**), set `pihole_exporter_setup_password` in vault.

Refresh Prometheus scrape targets after inventory changes:

{% raw %}
```bash
ansible-playbook playbooks/prometheus/deploy_prometheus_exporters.yml
```
{% endraw %}

This refresh command uses the repository's full combined inventory (`inventory/`); do not limit it to `inventory/dns/`, or exporter groups from other inventories will be omitted from that run.

Deploy the Pi-hole alert rules with the main Prometheus playbook, then refresh the exporter targets again:

{% raw %}
```bash
ansible-playbook -i inventory/prometheus/inventory.ini playbooks/prometheus/deploy_prometheus.yml
ansible-playbook playbooks/prometheus/deploy_prometheus_exporters.yml
```
{% endraw %}

Syntax-check the deployment playbook before applying changes:

{% raw %}
```bash
ansible-playbook -i inventory/dns/inventory.ini --syntax-check playbooks/prometheus/deploy_pihole_exporter.yml
```
{% endraw %}

---

## 🔔 Alert Rules

The `pihole` group in `prometheus.rules.yml` contains:

* `PiholeExporterDown` — the exporter cannot be scraped for 5 minutes (critical)
* `PiholeMetricsAbsent` — the exporter is up but returns no Pi-hole data for 10 minutes (warning)
* `PiholeBlockingDisabled` — blocking is disabled for 15 minutes (warning)
* `PiholeGravityEmpty` — the blocklist has no domains for 15 minutes (warning)

`prometheus.yml` does not currently have an `alerting:` section, so these alerts appear in Prometheus and Grafana but are not sent to Alertmanager.

---

## 🔍 Common Prometheus Queries

* Check that each exporter endpoint is reachable:
  `up{job="pihole_exporter"}`
* Check blocking status on each server:
  `pihole_status`
* Compare query load between the two servers:
  `pihole_dns_queries_today`
* Check the block rate:
  `pihole_ads_percentage_today`
* Check the cache hit ratio:
  `pihole_queries_cached / (pihole_queries_cached + pihole_queries_forwarded)`
* Find the busiest clients:
  `topk(10, max by (source, source_name) (pihole_top_sources))`
* Find the most blocked domains:
  `topk(10, max by (domain) (pihole_top_ads))`
* Check upstream response time:
  `pihole_forward_destinations_responsetime`

---

## 📊 Grafana Usage Notes

No Pi-hole dashboard is provisioned yet. The exporter project publishes one (grafana.com ID `10176`) that works with these metrics.

When building panels, group by `instance` rather than `hostname`, because `hostname` is `127.0.0.1` on both servers. Clients usually query both Pi-hole servers, so add the two servers' counts together for a network-wide total.

* * *

## 🛠️ Troubleshooting

### ❌ Exporter Target Is Down

Check:

* The `pihole_exporter` systemd service is active on the DNS host
* Port `9617` is reachable from Prometheus
* The target address matches the host's `global_ip_addresses` entry

### 📭 Target Is Up but There Is No Pi-hole Data

Check:

* `pihole-FTL` is running and the web API answers on port `80`
* The password in `/etc/pihole_exporter/password` is correct for this host
* The service logs for `401` or connection errors

This is the condition that triggers `PiholeMetricsAbsent`. If only one host is affected, its web password may differ from the other host's.

### 🚫 Blocking Disabled or Empty Blocklist

Check:

* `pihole status` on the host
* Re-enable blocking with `pihole enable` or in the web interface
* Rebuild the blocklist with `pihole -g` if `pihole_domains_being_blocked` is `0`

### 🛠️ Quick Verification Commands

{% raw %}
```bash
systemctl status pihole_exporter
journalctl -u pihole_exporter -n 50 --no-pager
curl -s http://localhost:9617/metrics | grep -E '^pihole_(status|domains_being_blocked)'
/usr/local/bin/pihole_exporter -version
```
{% endraw %}

---

## 🔐 Security & Operational Guidance

* Keep the Pi-hole password in Ansible vault; never put it in source-controlled plaintext
* Prefer a Pi-hole application password over the web interface password
* Restrict access to port `9617` to Prometheus and trusted administration hosts; the top-client and top-domain metrics reveal browsing activity on the network
* Protect `/etc/pihole_exporter/password`; it is readable only by root and the exporter's group
* Each exporter keeps one API session open; it closes the session when the service stops

---

## 🧾 Summary

`pihole_exporter` exposes Pi-hole query, blocking, client, and upstream metrics from each DNS server for Prometheus to scrape. Its alert rules flag a stopped exporter, disabled blocking, or an empty blocklist, while Node Exporter separately reports host-level health for the same servers.
