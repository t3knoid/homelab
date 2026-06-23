---
title: "Nginx Reverse Proxy Monitoring"
---

# 📊 Nginx Reverse Proxy Monitoring

This documentation covers the setup and deployment of Nginx reverse proxy monitoring using Prometheus and the [nginx-prometheus-exporter](https://github.com/nginx/nginx-prometheus-exporter). All deployment is managed through Ansible.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Components](#components)
4. [Deployment](#deployment)
5. [Configuration](#configuration)
6. [Ansible Playbook](#ansible-playbook)
7. [Scraping Metrics](#scraping-metrics)
8. [Verification](#verification)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The Nginx reverse proxy (rproxy) monitoring solution provides real-time visibility into reverse proxy performance and health. It collects metrics such as:

- Active connections and connection states
- Request rates and response codes
- Request/response throughput
- Cache hit/miss ratios
- Upstream server health

The monitoring stack consists of:

1. **nginx-prometheus-exporter** — Scrapes Nginx status and exports metrics in Prometheus format
2. **Local Nginx status endpoint** — Provides Nginx statistics via stub_status
3. **Prometheus server** — Collects and stores metrics from exporters
4. **Grafana dashboards** — Visualizes Nginx metrics

---

## Architecture

### Component Interaction

{% raw %}
```
┌─────────────────────────────────────────────────────────────┐
│ Reverse Proxy Host (rproxy)                                 │
│                                                             │
│  ┌──────────────────┐          ┌──────────────────────┐     │
│  │ Nginx Reverse    │          │ Local Nginx Status   │     │
│  │ Proxy (port 80)  ├─────-────┤ Endpoint (port 9114) │     │
│  └──────────────────┘          └──────────────────────┘     │
│           │                              ▲                  │
│           │                              │                  │
│  ┌────────┴──────────────────────────────┴──────────┐       │
│  │ nginx-prometheus-exporter (port 9113)            │       │
│  │ - Connects to localhost:9114/stub_status         │       │
│  │ - Exports Prometheus metrics on /metrics         │       │
│  └───────────────────────┬──────────────────────────┘       │
│                          │                                  │
└──────────────────────────┼──────────────────────────────────┘
                           │
                    [Metrics TCP 9113]
                           │
                           ▼
        ┌──────────────────────────────────┐
        │ Prometheus Server                │
        │ (port 9090)                      │
        │                                  │
        │ Scrapes nginx_exporter targets   │
        │ - Every 5 seconds                │
        └──────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────┐
        │ Grafana                          │
        │ (port 3000)                      │
        │                                  │
        │ Visualizes Nginx metrics         │
        └──────────────────────────────────┘
```
{% endraw %}

### Data Flow

1. Nginx reverse proxy logs connection and request statistics
2. Local Nginx status vhost exposes `/stub_status` endpoint
3. nginx-prometheus-exporter polls the status endpoint every second
4. Exporter converts text metrics to Prometheus format
5. Prometheus scrapes exporter on port 9113 every 5 seconds
6. Metrics are stored in Prometheus time-series database
7. Grafana queries Prometheus and displays dashboards

---

## Components

### 1. nginx-prometheus-exporter

The nginx-prometheus-exporter bridges Nginx status data and Prometheus.

**Role:** [roles/nginx_prometheus_exporter_setup](https://github.com/t3knoid/ansible/tree/main/roles/nginx_prometheus_exporter_setup)

**Key Features:**
- Converts Nginx metrics to Prometheus format
- Runs as dedicated systemd service
- Listens on port 9113 by default
- Scrapes internal Nginx status endpoint
- Minimal CPU/memory footprint

**Binary Details:**
- Version: 1.5.1
- Location: `/usr/local/bin/nginx-prometheus-exporter`
- User/Group: `nginx-prometheus-exporter:nginx-prometheus-exporter`
- Service: `nginx-prometheus-exporter.service`

### 2. Local Nginx Status Vhost

A dedicated Nginx virtual host exposes statistics via the stub_status module.

**Configuration:**
- Server name: `nginx-prometheus-exporter-status`
- Listen address: `127.0.0.1:9114`
- Status path: `/stub_status`
- Access: Localhost only (security)

**Nginx Config Template:** [roles/nginx_prometheus_exporter_setup/templates/nginx-prometheus-exporter-status.conf.j2](https://github.com/t3knoid/ansible/blob/main/roles/nginx_prometheus_exporter_setup/templates/nginx-prometheus-exporter-status.conf.j2)

### 3. Prometheus Configuration

Prometheus is configured to scrape nginx-prometheus-exporter targets.

**Scrape Job:**
- Job name: `nginx_exporter`
- Scrape interval: 5 seconds
- Metrics path: `/metrics`
- Port: 9113

**Prometheus Config Template:** [roles/prometheus_setup/templates/prometheus.yml.j2](https://github.com/t3knoid/ansible/blob/main/roles/nginx_prometheus_exporter_setup/templates/nginx-prometheus-exporter.service.j2)

---

## Deployment

### Prerequisites

- Ansible 2.9 or later
- Ubuntu 18.04 LTS or later on rproxy hosts
- Nginx already installed via `nginx_setup` role
- Prometheus server accessible for configuration updates

### Deployment Chain

The [deploy_rproxy.yml](playbooks/rproxy/deploy_rproxy.yml) playbook deploys the complete rproxy stack in this order:

{% raw %}
```yaml
roles:
  - global                           # Set up global variables and facts
  - nginx_setup                      # Install and configure Nginx
  - nginx_prometheus_exporter_setup  # Deploy exporter
  - rproxy_setup                     # Configure reverse proxy sites
```
{% endraw %}

### How to Deploy

**1. Run the deployment playbook:**

{% raw %}
```bash
ansible-playbook \
  -k \
  -i inventory/rproxy/inventory.ini \
  playbooks/rproxy/deploy_rproxy.yml
```
{% endraw %}

**2. Verify deployment:**

{% raw %}
```bash
ansible rproxy -i inventory/rproxy/inventory.ini -m systemd \
  -a "name=nginx-prometheus-exporter state=started"
```
{% endraw %}

**3. Test metrics endpoint:**

{% raw %}
```bash
curl http://rproxy-host:9113/metrics
```
{% endraw %}

---

## Configuration

### Inventory Configuration

Nginx exporter targets are defined in Prometheus inventory.

**File:** [inventory/prometheus/group_vars/all/main.yml](inventory/prometheus/group_vars/all/main.yml)

**Example Configuration:**

{% raw %}
```yaml
prometheus_setup_nginx_exporter_targets:
  - target: "rproxy-0:9113"
    labels:
      instance: "rproxy-0"
      site: "reverse-proxy"
  - target: "rproxy-1:9113"
    labels:
      instance: "rproxy-1"
      site: "reverse-proxy"
```
{% endraw %}

### Role Variables

**Role:** [roles/nginx_prometheus_exporter_setup/defaults/main/main.yml](roles/nginx_prometheus_exporter_setup/defaults/main.yml)

Key configurable variables:

| Variable | Default | Purpose |
|----------|---------|---------|
| `nginx_prometheus_exporter_setup_version` | `1.5.1` | Exporter version to deploy |
| `nginx_prometheus_exporter_setup_listen_address` | `0.0.0.0:9113` | Exporter listen address and port |
| `nginx_prometheus_exporter_setup_telemetry_path` | `/metrics` | Prometheus metrics endpoint path |
| `nginx_prometheus_exporter_setup_scrape_uri` | `http://127.0.0.1:9114/stub_status` | Nginx status endpoint URI |
| `nginx_prometheus_exporter_setup_user` | `nginx-prometheus-exporter` | Service user |
| `nginx_prometheus_exporter_setup_nginx_status_listen_address` | `127.0.0.1:9114` | Local status vhost listen address |

Override these in inventory `group_vars` if needed:

{% raw %}
```yaml
nginx_prometheus_exporter_setup_version: "1.6.0"
nginx_prometheus_exporter_setup_listen_address: "localhost:9113"
```
{% endraw %}

---

## Ansible Playbook

### Main Playbook: deploy_rproxy.yml

The primary deployment playbook for reverse proxies.

**File:** [playbooks/rproxy/deploy_rproxy.yml](playbooks/rproxy/deploy_rproxy.yml)

**Content:**

{% raw %}
```yaml
---
# Purpose: Sets up Reverse Proxy on rproxy hosts.

- name: Deploy Reverse Proxy
  hosts: rproxy
  become: true
  gather_facts: true
  roles:
    - global
    - nginx_setup
    - nginx_prometheus_exporter_setup
    - rproxy_setup
```
{% endraw %}

### Role Execution

**1. global role**
- Gathers system facts
- Sets up global variables (IP addresses, ports, etc.)

**2. nginx_setup role**
- Installs Nginx
- Configures base Nginx settings

**3. nginx_prometheus_exporter_setup role**
- Creates systemd user and group
- Downloads and installs exporter binary
- Creates local status vhost config
- Enables status vhost in Nginx
- Creates systemd service file
- Starts exporter service

**4. rproxy_setup role**
- Creates reverse proxy sites
- Applies SSL certificates
- Configures upstream targets
- Reloads Nginx with all configs

### Role Tasks

**File:** [roles/nginx_prometheus_exporter_setup/tasks/main.yml](https://github.com/t3knoid/ansible/blob/main/roles/nginx_prometheus_exporter_setup/tasks/main.yml)

Key tasks:

1. Create service user and group
2. Download and extract exporter binary
3. Create symlink for easy binary access
4. Set proper ownership and permissions
5. Template local Nginx status vhost config
6. Enable status vhost in Nginx
7. Validate Nginx configuration
8. Template systemd service file
9. Enable and start service

---

## Scraping Metrics

### Prometheus Scrape Configuration

Prometheus is configured via [roles/prometheus_setup/templates/prometheus.yml.j2](https://github.com/t3knoid/ansible/blob/main/roles/prometheus_setup/templates/prometheus.yml.j2)

**Nginx exporter scrape job:**

{% raw %}
```yaml
{% if prometheus_setup_nginx_exporter_targets | default([]) | length > 0 %}
  - job_name: 'nginx_exporter'
    scrape_interval: 5s

    static_configs:
{% for target in prometheus_setup_nginx_exporter_targets %}
      - targets: ['{{ target.target }}']
{% if target.labels is defined %}
        labels:
{% for key, value in target.labels.items() %}
          {{ key }}: '{{ value }}'
{% endfor %}
{% endif %}
{% endfor %}
{% endif %}
```
{% endraw %}

### How Targets are Passed to Prometheus

1. **Inventory defines targets** in [inventory/prometheus/group_vars/all/main.yml](inventory/prometheus/group_vars/all/main.yml):

   ```yaml
   prometheus_setup_nginx_exporter_targets:
     - target: "rproxy-0:9113"
       labels:
         instance: "rproxy-0"
   ```

2. **Prometheus playbook deploys with targets**:

   ```bash
   ansible-playbook \
     -i inventory/prometheus/inventory.ini \
     playbooks/prometheus/deploy_prometheus.yml
   ```

3. **Prometheus configuration template renders targets** using Jinja2 loops

4. **Prometheus service reloads** and begins scraping targets

### Exported Metrics

The nginx-prometheus-exporter exports these metric families:

| Metric | Type | Description |
|--------|------|-------------|
| `nginx_up` | Gauge | Whether Nginx is running (1) or down (0) |
| `nginx_requests_total` | Counter | Total requests processed |
| `nginx_connections_active` | Gauge | Active connections |
| `nginx_connections_reading` | Gauge | Connections reading requests |
| `nginx_connections_writing` | Gauge | Connections writing responses |
| `nginx_connections_waiting` | Gauge | Idle waiting connections |
| `nginx_connections_accepted_total` | Counter | Total accepted connections |
| `nginx_connections_handled_total` | Counter | Total handled connections |

Example query to check exporter status:

{% raw %}
```bash
curl http://rproxy-host:9113/metrics | grep nginx_up
```
{% endraw %}

---

## Verification

### 1. Check Service Status

On rproxy host:

{% raw %}
```bash
systemctl status nginx-prometheus-exporter
```
{% endraw %}

Expected output:

{% raw %}
```
● nginx-prometheus-exporter.service - Nginx Prometheus Exporter
     Loaded: loaded (/etc/systemd/system/nginx-prometheus-exporter.service; enabled; vendor preset: enabled)
     Active: active (running)
```
{% endraw %}

### 2. Verify Metrics Endpoint

{% raw %}
```bash
curl -s http://localhost:9113/metrics | head -20
```
{% endraw %}

Expected output (sample):

{% raw %}
```
# HELP nginx_up Whether the Nginx server is up
# TYPE nginx_up gauge
nginx_up 1
# HELP nginx_requests_total Total number of requests
# TYPE nginx_requests_total counter
nginx_requests_total 1234567
# HELP nginx_connections_active Active connections
# TYPE nginx_connections_active gauge
nginx_connections_active 42
```
{% endraw %}

### 3. Verify Local Status Endpoint

{% raw %}
```bash
curl -s http://127.0.0.1:9114/stub_status
```
{% endraw %}

Expected output:

{% raw %}
```
Active connections: 42
server accepts handled requests
 1234567 1234567 1234567
Reading: 2 Writing: 5 Waiting: 35
```
{% endraw %}

### 4. Verify Nginx Status Vhost

{% raw %}
```bash
curl -I http://127.0.0.1:9114/
```
{% endraw %}

Expected output:

{% raw %}
```
HTTP/1.1 200 OK
Server: nginx/1.18.0
Content-Type: text/plain
```
{% endraw %}

### 5. Check Prometheus Targets

Access Prometheus web UI: `http://prometheus-host:9090/targets`

Look for `nginx_exporter` job. Expected state: **UP**

### 6. Query Prometheus

In Prometheus query interface, run:

{% raw %}
```
nginx_up
```
{% endraw %}

Expected result: Returns 1 for each exporter target

---

## Troubleshooting

### Issue: Service Fails to Start

**Symptom:** `systemctl status nginx-prometheus-exporter` shows failed state

**Check logs:**

{% raw %}
```bash
journalctl -u nginx-prometheus-exporter -n 50
```
{% endraw %}

**Common causes:**

1. **Port already in use** — Change `nginx_prometheus_exporter_setup_listen_address` in inventory
2. **Binary download failed** — Check internet connectivity and GitHub releases availability
3. **Permissions issue** — Ensure service user exists with correct permissions:

   ```bash
   getent passwd nginx-prometheus-exporter
   ls -la /usr/local/bin/nginx-prometheus-exporter
   ```

### Issue: Cannot Connect to Metrics Endpoint

**Symptom:** `curl: (7) Failed to connect to localhost port 9113`

**Check if service is running:**

{% raw %}
```bash
netstat -tlnp | grep 9113
```
{% endraw %}

**Check service status:**

{% raw %}
```bash
systemctl status nginx-prometheus-exporter
```
{% endraw %}

**Manual test of exporter:**

{% raw %}
```bash
sudo -u nginx-prometheus-exporter /usr/local/bin/nginx-prometheus-exporter \
  -nginx.scrape-uri=http://127.0.0.1:9114/stub_status
```
{% endraw %}

### Issue: Metrics Show 0 or Missing Data

**Symptom:** Prometheus scrapes successfully but metrics are zeros or incomplete

**Check local Nginx status endpoint:**

{% raw %}
```bash
curl -s http://127.0.0.1:9114/stub_status
```
{% endraw %}

If no output, check:

1. **Nginx status vhost enabled:**

   ```bash
   ls -la /etc/nginx/sites-enabled/nginx-prometheus-exporter-status.conf
   ```

2. **Nginx configuration valid:**

   ```bash
   nginx -t
   ```

3. **Nginx reloaded after status vhost setup:**

   ```bash
   systemctl reload nginx
   ```

### Issue: Prometheus Shows Target as DOWN

**Symptom:** Prometheus targets page shows `nginx_exporter` job as RED (DOWN)

**Check exporter is accessible:**

{% raw %}
```bash
curl -v http://rproxy-host:9113/metrics
```
{% endraw %}

**Check Prometheus logs:**

{% raw %}
```bash
journalctl -u prometheus -n 50
```
{% endraw %}

**Verify firewall rules:**

{% raw %}
```bash
sudo ufw status | grep 9113
```
{% endraw %}

If blocked, allow port:

{% raw %}
```bash
sudo ufw allow 9113/tcp
```
{% endraw %}

### Issue: High CPU Usage from Exporter

**Symptom:** nginx-prometheus-exporter process consuming excessive CPU

**Check exporter logs for errors:**

{% raw %}
```bash
journalctl -u nginx-prometheus-exporter -f
```
{% endraw %}

**Reduce scrape frequency in Prometheus config:**

{% raw %}
```yaml
scrape_interval: 15s  # Increase from 5s to 15s
```
{% endraw %}

Then redeploy Prometheus.

### Issue: Exporter Exits Immediately After Start

**Symptom:** Service starts then stops within seconds

**Check for startup errors:**

{% raw %}
```bash
/usr/local/bin/nginx-prometheus-exporter \
  -nginx.scrape-uri=http://127.0.0.1:9114/stub_status
```
{% endraw %}

**Common causes:**

1. **Invalid scrape URI** — Verify stub_status endpoint is accessible
2. **Binary incompatibility** — Check CPU architecture:

   ```bash
   file /usr/local/bin/nginx-prometheus-exporter
   uname -m
   ```

3. **Missing dependencies** — Check required libraries:

   ```bash
   ldd /usr/local/bin/nginx-prometheus-exporter
   ```

---

## Summary

The Nginx Prometheus monitoring solution provides comprehensive visibility into reverse proxy performance through:

1. **Automated deployment** via Ansible playbooks
2. **Real-time metrics** from nginx-prometheus-exporter
3. **Centralized storage** in Prometheus
4. **Dashboard visualization** in Grafana

Use this documentation to deploy, configure, and troubleshoot Nginx monitoring.