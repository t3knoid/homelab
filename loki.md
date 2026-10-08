---
title: "Loki"
---

# 🔥 **Loki**

Grafana Loki is the homelab's centralized log storage and query service. It is deployed as a single Linux service and is designed to work alongside [Grafana](https://homelab.refol.us/grafana.html) for exploring logs. Loki indexes log labels rather than the full contents of every log line, keeping storage and queries efficient.

Loki is deployed and managed using [Ansible](https://homelab.refol.us/ansible.html). Deploying Loki provides the backend; a log collector must also be configured on log-producing hosts to send entries to it.

---

## 🎯 **Purpose**

Loki provides one place to search and correlate logs from homelab services. It complements [Prometheus](https://homelab.refol.us/prometheus.html): Prometheus stores metrics, while Loki stores log lines. Together, they let operators move between a metric or alert and the related service logs in Grafana.

The current Ansible configuration deploys the Loki server, but does not configure log shippers or provision Loki as a Grafana datasource. Logs will not appear until those integrations are configured.

---

## 🔄 **How Loki Works**

Loki uses a push-based ingestion model:

{% raw %}
```text
Hosts and services → Log collector → Loki → Grafana Explore and dashboards
```
{% endraw %}

- **Log sources** produce system or application logs.
- **Log collectors** discover and read logs, attach labels, and push batches to Loki.
- **Loki** stores log chunks and a compact index of their labels.
- **Grafana** sends LogQL queries to Loki and displays matching log lines.

Collectors must be configured with Loki's push endpoint, `http://192.168.20.193:3100/loki/api/v1/push`, and suitable labels. The endpoint is private-network access; Loki's built-in authentication is disabled, so it should not be exposed directly to the internet.

---

## 🧩 **Key Components**

### 🏛️ **1. Loki Server**

- Runs on `loki-0` (`192.168.20.193`).
- Listens for HTTP requests on port `3100` and gRPC on port `9096`.
- Uses the filesystem object store and a local TSDB index under `/loki`.
- Runs as the `loki` system user, managed by systemd.
- Retention is disabled in the current configuration; monitor `/loki` disk usage.

### 📦 **2. Log Collectors**

Collectors such as Grafana Alloy run near the logs, attach useful labels (for example `host`, `job`, and `service`), and push entries to Loki. No collector is currently deployed by this repository, so ingestion depends on configuring one separately.

### 📐 **3. LogQL**

LogQL selects streams by labels and can filter or parse their log lines. For example, if a collector sends logs with a `job="varlogs"` label:

{% raw %}
```logql
{job="varlogs"}
{job="varlogs"} |= "error"
```
{% endraw %}

Use the labels actually emitted by the configured collector; `job="varlogs"` is an example, not a preconfigured stream in this homelab.

---

## ⚙️ **Deployment**

Deploy Loki with the repository playbook:

{% raw %}
```bash
ansible-playbook -k -i inventory/loki/inventory.ini playbooks/loki/deploy_loki.yml
```
{% endraw %}

The `loki_setup` role installs the pinned Loki release, renders `/loki/etc/loki.yml`, creates its local storage directories, and enables the systemd service. The server's private HTTP URL for Grafana or collectors is `http://192.168.20.193:3100`.

---

## ✅ **Using and Verifying Loki**

Check that the service is ready:

{% raw %}
```bash
curl -f http://192.168.20.193:3100/ready
```
{% endraw %}

To explore logs in Grafana, configure a Loki datasource with URL `http://192.168.20.193:3100` and select it in Explore. The current Grafana Ansible provisioning defines Prometheus only, so adding the Loki datasource requires a provisioning change or a separate Grafana configuration.

Once a collector is sending logs, query a stream using its labels in Grafana Explore, or check Loki's label API:

{% raw %}
```bash
curl http://192.168.20.193:3100/loki/api/v1/labels
```
{% endraw %}

An empty label list is expected until log ingestion has been configured and data received.

---

## 🔗 **Relevant Links**

### 📘 **Official Documentation**

- [Grafana Loki](https://grafana.com/oss/loki/)
- [Loki documentation](https://grafana.com/docs/loki/latest/)
- [LogQL](https://grafana.com/docs/loki/latest/query/)
- [Grafana Alloy](https://grafana.com/docs/alloy/latest/)

### 🏠 **Homelab**

- [Grafana](https://homelab.refol.us/grafana.html)
- [Prometheus](https://homelab.refol.us/prometheus.html)
- [Ansible](https://homelab.refol.us/ansible.html)
