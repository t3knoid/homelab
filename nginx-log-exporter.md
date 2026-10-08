---
title: "Nginx-log-exporter"
---

# Nginx-log-exporter

## 🎯 Purpose

NGINX Log Exporter converts completed nginx access-log entries into Prometheus metrics for per-domain traffic analysis in Grafana. Use it to monitor:

- Request volume and the most requested domains.
- HTTP response classes, including client and server errors.
- Response bytes and request-duration distributions.
- Traffic trends on the main reverse proxy, `rproxy-0`.

Unlike [NGINX Prometheus Exporter](https://homelab.refol.us/nginx-prometheus-exporter.html), which reads `stub_status` for global request and connection metrics, this
exporter reads access logs to identify which domains receive requests. The two exporters complement each other; neither replaces the other.

## 🏗 Architecture

- Nginx writes a dedicated traffic log on `rproxy-0`.
- `prometheus-nginxlog-exporter` tails that log and exposes metrics on port `4040`.
- `prometheus-0` scrapes the exporter every 15 seconds using the
  `nginxlog_exporter` job.
- Grafana reads the metrics through its existing Prometheus datasource.

| Component | Configuration |
| --- | --- |
| Exporter host | `rproxy-0`, `192.168.30.210` |
| Exporter version | `1.11.0` |
| Systemd service and user | `nginxlog-exporter` |
| Metrics endpoint | `http://192.168.30.210:4040/metrics` |
| Exporter configuration | `/etc/prometheus-nginxlog-exporter.hcl` |
| Nginx logging configuration | `/etc/nginx/conf.d/nginxlog-exporter.conf` |
| Dedicated traffic log | `/data/nginx/log/traffic.log` |
| Log rotation | Daily, seven retained files |
| Inventory group | `nginxlog_exporter`, containing the main proxy |
| Ansible role | `nginxlog_exporter_setup` |

The exporter binds to the proxy's private IP, not the loopback address. Access to port `4040` should be limited to the monitoring network or Prometheus host.

## 📊 What the Exporter Provides

| Metric | Purpose |
| --- | --- |
| `nginxlog_http_response_count_total` | Completed HTTP request counter |
| `nginxlog_http_response_size_bytes` | Cumulative response bytes |
| `nginxlog_http_response_time_seconds` | Request-duration summary |
| `nginxlog_http_response_time_seconds_hist_bucket` | Request-duration histogram buckets |
| `nginxlog_http_response_time_seconds_hist_sum` | Cumulative request duration |
| `nginxlog_http_response_time_seconds_hist_count` | Number of duration observations |
| `nginxlog_parse_errors_total` | Access-log lines that could not be parsed |

Traffic metrics include `domain`, `method`, and `status` labels. Histogram
buckets also have an `le` label. Prometheus supplies `job` and `instance`.
`nginxlog_http_response_size_bytes` is a counter despite lacking a `_total` suffix.

### 📊 Traffic Log Format

The role adds this nginx log format:

{% raw %}
```nginx
log_format rproxy_metrics '$server_name "$request_method / $server_protocol" $status $body_bytes_sent $request_time'; access_log /data/nginx/log/traffic.log rproxy_metrics;
```
{% endraw %}

The request path is deliberately replaced with `/`. The dedicated log contains the configured server name, method, protocol, status, response bytes, and duration. It does not record client IPs, actual paths, query strings, cookies, or authorization headers. Existing nginx logs are not changed by this format.

The `domain` label comes from `$server_name`, rather than an arbitrary incoming Host header. This keeps labels bounded by nginx's configured sites.

## ⚙️ Prerequisites

- Nginx installed and configured on the main reverse proxy.
- The `rproxy-0` host included in the inventory's `nginxlog_exporter` group.
- The exporter service able to read the dedicated traffic log through `www-data` membership.
- Network access from Prometheus to the proxy's private IP on port `4040`.
- A Prometheus scrape target for the `nginxlog_exporter` job.
- Grafana connected to the existing Prometheus datasource.

## 🚀 Deployment

Run these commands from the Ansible repository with its Python environment active:

{% raw %}
```bash
source /opt/python_3.12/bin/activate
```
{% endraw %}

Deploy the log exporter and its nginx logging configuration:

{% raw %}
```bash
ansible-playbook -i inventory/rproxy/inventory.ini -k -u ansible playbooks/prometheus/deploy_nginxlog_exporter.yml
```
{% endraw %}

Refresh Prometheus exporter targets using the default combined inventory:

{% raw %}
```bash
ansible-playbook -k -u ansible playbooks/prometheus/deploy_prometheus_exporters.yml
```
{% endraw %}

Do not scope the scrape refresh to the Grafana inventory or limit it to `rproxy-0`. It runs on the Prometheus host and merges inventory targets with previously registered targets.

Deploy the Grafana dashboard:

{% raw %}
```bash
ansible-playbook -i inventory/grafana/inventory.ini -k playbooks/grafana/deploy_grafana.yml
```
{% endraw %}

Syntax check:

{% raw %}
```bash
ansible-playbook --syntax-check -i inventory/rproxy/inventory.ini playbooks/prometheus/deploy_nginxlog_exporter.yml
```
{% endraw %}

The exporter deployment playbook includes `global`, `nginx_setup`, and `nginxlog_exporter_setup`. It validates the exporter configuration and runs `nginx -t` before applying its pending nginx reload.

## Prometheus Queries

Exporter health:

{% raw %}
```promql
up{job="nginxlog_exporter",instance="rproxy-0"}
```
{% endraw %}

Request rate by domain:

{% raw %}
```promql
sum by (domain) (rate(nginxlog_http_response_count_total{job="nginxlog_exporter",instance="rproxy-0"}[5m]))
```
{% endraw %}

Most requested domain during the last hour:

{% raw %}
```promql
topk(1, sum by (domain) (increase(nginxlog_http_response_count_total{job="nginxlog_exporter",instance="rproxy-0"}[1h])) > 0)
```
{% endraw %}

Top eight domains during the last hour:

{% raw %}
```promql
sort_desc(topk(8, sum by (domain) (increase(nginxlog_http_response_count_total{job="nginxlog_exporter",instance="rproxy-0"}[1h])) > 0))
```
{% endraw %}

Server-error rate by domain:

{% raw %}
```promql
sum by (domain) (rate(nginxlog_http_response_count_total{job="nginxlog_exporter",instance="rproxy-0",status=~"5.."}[5m]))
```
{% endraw %}

95th-percentile request duration by domain:

{% raw %}
```promql
histogram_quantile(0.95, sum by (domain, le) (rate(nginxlog_http_response_time_seconds_hist_bucket{job="nginxlog_exporter",instance="rproxy-0"}[5m])))
```
{% endraw %}

Response bytes per second by domain:

{% raw %}
```promql
sum by (domain) (rate(nginxlog_http_response_size_bytes{job="nginxlog_exporter",instance="rproxy-0"}[5m]))
```
{% endraw %}

Recent parsing errors:

{% raw %}
```promql
increase(nginxlog_parse_errors_total{job="nginxlog_exporter",instance="rproxy-0"}[5m])
```
{% endraw %}

## Grafana Dashboard Recommendations

The Observability Landing dashboard, `/d/observability-landing`, includes:

- HTTP Traffic / All Sites: request-rate bars from the existing nginx status exporter.
- Requests / Selected Window: estimated total requests during the selected time range.
- Most Requested Domain: leading domain and its estimated completed-request count.
- Top Domains / Request Volume: horizontal bars ranking the busiest domains.
- HTTP Request Duration / Histogram: duration heatmap across all sites.
- HTTP Responses: stacked request rates grouped into response classes.

Domain rankings use the selected dashboard time range. Allow several scrape intervals before expecting rate and increase queries to return useful data. Domain traffic history starts after collector deployment; existing access logs are not used to reconstruct earlier traffic.

## Operational Checks

On `rproxy-0`, check the service and recent diagnostics:

{% raw %}
```bash
systemctl status nginxlog-exporter
journalctl -u nginxlog-exporter -n 50 --no-pager
```
{% endraw %}

Check exporter metrics using its private-IP listener:

{% raw %}
```bash
curl -fsS http://192.168.30.210:4040/metrics
```
{% endraw %}

Validate nginx and inspect the dedicated log after visiting a site:

{% raw %}
```bash
nginx -t
tail -n 10 /data/nginx/log/traffic.log
```
{% endraw %}

In Prometheus, confirm `up{job="nginxlog_exporter",instance="rproxy-0"}` is `1`. Look for `domain` labels on `nginxlog_http_response_count_total` and ensure
`nginxlog_parse_errors_total` does not increase during normal operation.

## Troubleshooting

**No data in Grafana:**

- Check the Prometheus target, exporter service, and access to port `4040`.
- Confirm the datasource and `job`/`instance` labels match the queries.
- Visit a site and allow several scrape intervals for samples to accumulate.
- Check the selected dashboard time range includes traffic collected after deployment.

**Exporter up, but a domain is missing:**

- Confirm completed requests appear in `/data/nginx/log/traffic.log`.
- Check the site's configured `server_name`; aliases may share that label.
- A server or location with its own `access_log` directive overrides inherited
  HTTP-context logging. Add the `rproxy_metrics` access log at that level too.
- Long-lived streams are logged when the request completes, not when it begins.

**Parsing errors increase:**

- Check exporter logs for the rejected line and compare nginx/exporter formats.
- Keep the dedicated log separate from standard combined-format logs.
- Ensure custom logging changes preserve the fields expected by the exporter.

**Traffic totals do not match the global nginx counter:**

- The status exporter counts global requests; the log exporter counts completed
  requests in the dedicated log. They observe different points in request handling.
- Both include monitoring probes; neither represents only human visitors.
- Prometheus `increase` estimates changes between scrapes. These are operational
  trends, not billing-grade exact totals.

## Best Practices

- Keep the metrics endpoint private and restrict network access appropriately.
- Use configured server names as domain labels; avoid URLs and client IP labels.
- Retain the privacy-preserving log format and daily rotation.
- Monitor exporter health and parsing errors alongside traffic volume.
- Keep the existing nginx status exporter for independent reachability and connection monitoring.
- Verify site-level logging overrides whenever adding or changing proxy sites.

## Summary

NGINX Log Exporter adds per-domain request volume, response status, and latency
visibility to the main reverse proxy. Together with nginx's status exporter,
Prometheus, and Grafana, it shows overall load and which domains receive the
most traffic without collecting client addresses or request URLs in the
dedicated metrics log.
