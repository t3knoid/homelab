---
title: "Nginx Reverse Proxy Cluster"
---

# Nginx Reverse Proxy Cluster

The Nginx Reverse Proxy Cluster serves as the public gateway into the homelab’s internal services. It abstracts internal topology, centralizes TLS termination, enforces security policies, and improves performance through caching and request routing. The cluster is composed of a **frontend Nginx server** and two redundant **backend proxy nodes**, forming a resilient and maintainable ingress layer.

---

## 🗺️ Architecture Overview (ASCII Diagram)

```
                          ┌───────────────────────────┐
                          │         Internet          │
                          └──────────────┬────────────┘
                                         │
                                         ▼
                          ┌───────────────────────────┐
                          │    Frontend Nginx Proxy   │
                          │ (TLS termination, routing)│
                          └──────────────┬────────────┘
                                         │
                                 Upstream "backend"
                                         │
                 ┌───────────────────────┴────────────────────────┐
                 │                                                │
                 ▼                                                ▼
    ┌────────────────────────┐                     ┌────────────────────────┐
    │     Backend Proxy 1    │                     │     Backend Proxy 2    │
    │   (Primary / Active)   │                     │  (Passive / Failover)  │
    └────────────┬───────────┘                     └────────────┬───────────┘
                 │                                              │
                 └──────────────┬───────────────────────────────┘
                                │
                                ▼
                  ┌──────────────────────────┐
                  │  Internal Web Services   │
                  │ (No SSL – Trust Boundary)│
                  └──────────────────────────┘
```

---

## 🖥️ Frontend Server Configuration

The frontend server uses an Nginx upstream block to define the backend cluster. Traffic is routed to the first server listed unless it becomes unreachable, at which point Nginx automatically promotes the backup node.

```nginx
http {
    # BEGIN ANSIBLE MANAGED BLOCK
    upstream backend {
        server rproxy-1:80 max_fails=3 fail_timeout=5s;
        server rproxy-2:80 backup;
    }
    # END ANSIBLE MANAGED BLOCK
}
```

Example virtual host configuration (TLS termination happens here):

```nginx
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;

    server_name homelab.refol.us;
    ssl_certificate     /data/certs/homelab.refol.us/fullchain.pem;
    ssl_certificate_key /data/certs/homelab.refol.us/privkey.pem;

    index index.html index.htm index.php;

    location / {
        proxy_pass http://backend;
    }
}
```

---

## ⚙️ Backend Server Configuration

Backend servers are identical. They operate purely as reverse proxies to internal applications—no SSL, no domain logic, no routing complexity.

```nginx
location / {
    proxy_pass http://192.168.2.186:80;
}
```

This consistency allows either backend node to assume full responsibility during failover.

---

## 💠 High Availability Strategy (HA)

The reverse-proxy cluster implements an **active–passive HA model**:

### **Active Node**

* Receives all traffic under normal conditions
* Performs forwarding to internal services

### **Passive Node**

* Stays warm and ready
* Automatically activated via Nginx upstream health checks

### **Failure Detection**

Nginx monitors each backend with:

* `max_fails=3`
* `fail_timeout=5s`

If the primary fails to respond or exceeds failure thresholds, traffic is immediately shifted to the backup.

### **Recovery**

Once the primary node becomes healthy again, Nginx gradually resumes routing traffic back without downtime or manual intervention.

### **Benefits**

* Zero external change during backend node failure
* No need for shared IP or VRRP due to frontend-based decision-making
* Upgrades can be performed with minimal disruption by draining traffic to the backup

---

## 🎯 Why This Design?

This architecture was selected for the homelab due to its strong balance of **simplicity**, **resilience**, and **maintainability**:

### **1. Clear Separation of Responsibilities**

* Frontend handles TLS, routing, caching, and public ingress
* Backends focus solely on efficient proxy operations
* Internal services remain clean and configuration-light

### **2. Built-In Redundancy Without Extra Complexity**

No need for:

* Keepalived
* VRRP
* Consul
* External load balancers

The upstream block alone provides transparent failover.

### **3. Reduced Attack Surface**

Only the frontend server is publicly exposed, minimizing exposure of:

* Internal IPs
* Backend ports
* Application servers

### **4. Simplified Certificate and Domain Management**

All SSL certificates are managed in one place—easier renewals, updates, and automation.

### **5. Scalable and Homelab-Friendly**

New backend nodes can be added or removed without major architectural changes.
Ideal for a homelab where services evolve frequently.

### **6. Cloud-Service-Like Architecture**

The design mirrors industry-standard ingress layers used in:

* Kubernetes clusters
* Cloud load balancers (AWS ALB, GCP HTTPS LB)
* Enterprise DMZ architectures

This makes it both educational and practical.