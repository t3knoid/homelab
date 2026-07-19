---
title: "Blackbox Exporter Usage Guide"
---

# 🚦 Blackbox Exporter Usage Guide

## 🎯 Overview  
Prometheus Blackbox Exporter probes endpoints over network protocols (HTTP, HTTPS, TCP, ICMP, DNS) and exposes probe results as Prometheus metrics. Unlike node‑level exporters, it measures service reachability and response characteristics from the perspective of the probe host.

## 📌 Common Use Cases  
- Website/API uptime checks  
- TLS certificate expiration monitoring  
- DNS resolution verification  
- TCP port availability checks  
- ICMP reachability (ping)

## 🧭 How It Works  
1. Prometheus calls Blackbox Exporter’s `/probe` endpoint.  
2. Prometheus passes `target` and `module` parameters.  
3. Blackbox Exporter performs the probe and returns metrics.  
4. Prometheus stores metrics for alerting and dashboards.

## 🧩 Key Components  
- **Blackbox Exporter:** Probe engine and metric endpoint  
- **Modules:** Probe definitions in `blackbox.yml` (e.g., `http_2xx`, `tcp_connect`, `icmp`)  
- **Prometheus scrape config:** Uses relabeling to map targets/modules into probe requests  
- **Alert rules:** Detect failed checks or degraded probe behavior

## 🛠 Example Blackbox Module Config (`blackbox.yml`)  
{% raw %}
```yaml
modules:
  http_2xx:
    prober: http
    timeout: 5s
    http:
      method: GET
      preferred_ip_protocol: ip4
      valid_status_codes: [200, 301, 302]

  tcp_connect:
    prober: tcp
    timeout: 5s

  icmp:
    prober: icmp
    timeout: 5s
    preferred_ip_protocol: ip4
```
{% endraw %}

## ⚙️ Example Prometheus Scrape Config  
### HTTP probe  
{% raw %}
```yaml
scrape_configs:
  - job_name: blackbox_http
    metrics_path: /probe
    params:
      module: [http_2xx]
    static_configs:
      - targets:
        - https://example.com
        - https://grafana.example.com
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: blackbox-exporter:9115
```
{% endraw %}

### TCP probe  
{% raw %}
```yaml
  - job_name: blackbox_tcp
    metrics_path: /probe
    params:
      module: [tcp_connect]
    static_configs:
      - targets:
        - postgres.example.com:5432
        - redis.example.com:6379
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: blackbox-exporter:9115
```
{% endraw %}

## 📊 Important Metrics  
- **probe_success** — 1 = probe passed, 0 = failed  
- **probe_duration_seconds** — end‑to‑end probe duration  
- **probe_http_status_code** — returned HTTP status code  
- **probe_ssl_earliest_cert_expiry** — earliest TLS cert expiry timestamp  
- **probe_dns_lookup_time_seconds** — DNS resolution time

## 🔍 Sample PromQL Queries  
{% raw %}
```promql
avg_over_time(probe_success[5m])
probe_success == 0
histogram_quantile(0.95, sum(rate(probe_duration_seconds_bucket[15m])) by (le, instance))
(probe_ssl_earliest_cert_expiry - time()) / 86400
```
{% endraw %}

## 🚨 Example Alerts  
{% raw %}
```yaml
groups:
  - name: blackbox.rules
    rules:
      - alert: BlackboxProbeFailed
        expr: probe_success == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Probe failed for {{ $labels.instance }}"
          description: "Blackbox probe has been failing for 5 minutes."

      - alert: BlackboxHighLatency
        expr: probe_duration_seconds > 2
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High probe latency for {{ $labels.instance }}"
          description: "Probe duration is above 2s for 10 minutes."

      - alert: CertificateExpiringSoon
        expr: (probe_ssl_earliest_cert_expiry - time()) < 86400 * 14
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "Certificate expiring soon for {{ $labels.instance }}"
          description: "TLS certificate will expire in less than 14 days."
```
{% endraw %}

## 🚀 Deployment

Blackbox Exporter is deployed using Ansible.

### Prerequisites
- Inventory contains the target host group for Blackbox Exporter.
- Required base roles are available in the repository.
- SSH access and privilege escalation are configured for target hosts.

### Recommended Playbook Pattern
Use the same role ordering pattern used across this repository:

- global
- users
- prerequisite roles such as docker_setup when required by the role implementation
- blackbox exporter setup role

Example:

    ---
    - name: Deploy Blackbox Exporter
      hosts: blackbox
      become: true
      roles:
        - global
        - users
        - docker_setup
        - blackbox_exporter_setup

### Validate Before Deploy
Run a syntax check first:

    ansible-playbook -i inventory/<env>/inventory.ini playbooks/<domain>/deploy_blackbox_exporter.yml --syntax-check

### Deploy
Run the playbook:

    ansible-playbook -i inventory/<env>/inventory.ini playbooks/<domain>/deploy_blackbox_exporter.yml

### Post-Deployment Validation
Health check:

    curl http://<blackbox-host>:9115/-/healthy

Probe test:

    curl "http://<blackbox-host>:9115/probe?target=https://example.com&module=http_2xx"

### Operational Verification
- Prometheus target for Blackbox Exporter is UP.
- probe_success equals 1 for expected targets.
- Alert rules are loaded and evaluating.
- Network policy/firewall allows Prometheus to reach port 9115.

See also: **[Adding Blackbox Exporter Targets](adding_blackbox_exporter_targets.md)**

## 🧪 Operational Tips  
- Keep probe timeouts realistic (e.g., `5s`)  
- Separate jobs/modules by protocol  
- Use labels for environment and ownership  
- ICMP probes require privileges  
- Start with `probe_success` alerts, then add latency and certificate alerts

## 🛠 Troubleshooting  
- Check exporter health: `http://<blackbox-host>:9115/-/healthy`  
- Test probe manually:  
  `http://<blackbox-host>:9115/probe?target=https://example.com&module=http_2xx`  
- Verify relabeling (`__param_target`, `__address__`)  
- Confirm DNS/connectivity from exporter host

## 🔐 Security Considerations  
- Restrict access to exporter endpoint  
- Avoid exposing probe endpoints publicly  
- Be careful probing internal‑only services  
- Use HTTPS and authentication where possible

## 📝 Summary  
Blackbox Exporter extends observability from host metrics to real network/service checks. A solid baseline includes:

- HTTP + TCP probes  
- `probe_success` and latency alerts  
- TLS expiry monitoring  
- Clear module/job separation