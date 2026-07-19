---
title: "Nginx‑prometheus‑exporter"
---

# 📈 Nginx‑prometheus‑exporter

## 🎯 Purpose  
NGINX Prometheus Exporter converts NGINX status data into Prometheus metrics so you can visualize web server health in Grafana and alert on failures later. Use it to monitor:  
- Whether NGINX is reachable  
- Connection load and behavior  
- Request throughput trends  
- Early signs of saturation or errors

## 🏗 Architecture  
- NGINX exposes status data (typically via a status endpoint).  
- NGINX Exporter scrapes that endpoint.  
- Prometheus scrapes NGINX Exporter.  
- Grafana reads metrics from Prometheus.

## 📊 What the Exporter Provides  
Common metric families include:  
- nginx_up  
- nginx_connections_active  
- nginx_connections_reading  
- nginx_connections_writing  
- nginx_connections_waiting  
- nginx_connections_accepted  
- nginx_connections_handled  
- nginx_http_requests_total

## ⚙️ Prerequisites  
- NGINX installed and running on target host  
- NGINX status endpoint enabled and reachable by exporter  
- Exporter service running on expected port  
- Prometheus scrape target configured for `nginx_exporter` job  
- Grafana datasource connected to Prometheus

## 🚀 Deployment
Example deployment flow:

Deploy or refresh reverse proxy hosts:  
{% raw %}
```bash
source /opt/python_3.12/bin/activate
ansible-playbook -i inventory/rproxy/inventory.ini playbooks/rproxy/deploy_rproxy.yml
```
{% endraw %}

Refresh Prometheus exporter targets:  
{% raw %}
```bash
source /opt/python_3.12/bin/activate
ansible-playbook -i inventory/rproxy/inventory.ini playbooks/prometheus/deploy_prometheus_exporters.yml
```
{% endraw %}

Syntax check:  
{% raw %}
```bash
source /opt/python_3.12/bin/activate
ansible-playbook --syntax-check -i inventory/rproxy/inventory.ini playbooks/rproxy/deploy_rproxy.yml
```
{% endraw %}

👉 See also: **[Adding NGINX Exporter to an Inventory](adding_nginx_exporter_to_an_inventory.md)**

## 🔍 Prometheus Queries  
Exporter health:  
{% raw %}
```promql
up{job="nginx_exporter"}
```
{% endraw %}

NGINX reachability:  
{% raw %}
```promql
nginx_up
```
{% endraw %}

Active connections:  
{% raw %}
```promql
nginx_connections_active
```
{% endraw %}

Request rate:  
{% raw %}
```promql
rate(nginx_http_requests_total[5m])
```
{% endraw %}

Total active connections:  
{% raw %}
```promql
sum(nginx_connections_active)
```
{% endraw %}

Top busy instances:  
{% raw %}
```promql
topk(5, nginx_connections_active)
```
{% endraw %}

## 📈 Grafana Dashboard Recommendations  
Panels:  
- Exporter Up (stat)  
- NGINX Up (stat)  
- Active Connections (time series)  
- Request Rate (time series)  
- Connection States (stacked)  
- Instance Table  

Variables: instance, group/environment, time range presets.

## 🧪 Operational Checks  
On a target host:

Check exporter service:  
{% raw %}
```bash
systemctl status nginx-prometheus-exporter
```
{% endraw %}

Check exporter metrics:  
{% raw %}
```bash
curl -s http://127.0.0.1:<exporter_port>/metrics | head
```
{% endraw %}

Check NGINX status endpoint:  
{% raw %}
```bash
curl -s http://127.0.0.1:<nginx_status_port_or_path>
```
{% endraw %}

## 🛠 Troubleshooting  
**No data in Grafana:**  
- Prometheus target down  
- Exporter not running  
- Exporter cannot reach NGINX  
- Wrong datasource/job labels  

**Exporter up but nginx_up = 0:**  
- Status endpoint unreachable  
- Firewall/ACL blocking  
- Wrong scrape URI  

**Intermittent drops:**  
- Network instability  
- NGINX reload windows  
- Host resource pressure

## ⭐ Best Practices  
- Restrict status endpoint  
- Use consistent instance labels  
- Track both exporter health and nginx_up  
- Add recording rules for high‑traffic environments

## 📝 Summary  
NGINX Exporter provides lightweight visibility into NGINX health using Prometheus and Grafana. Start with exporter health, reachability, and connection/request trends, then layer alerting.