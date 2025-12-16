# Nginx Reverse Proxy Cluster with OAuth2 Integration

The Nginx reverse-proxy cluster forms the front line of the homelab’s application delivery architecture. It abstracts internal services, offloads TLS/SSL operations, provides intelligent load distribution, and now enforces **centralized authentication via OAuth2 Proxy with Microsoft Entra ID** for services that require identity-aware access.

A primary frontend node terminates HTTPS traffic, performs OAuth2 authentication checks when needed, and routes requests to one of two backend Nginx servers. Backend nodes provide redundancy, delivering highly available and fault-tolerant service delivery.

---

## 🏗️ Frontend Server Configuration (with OAuth2 Support)

The primary frontend Nginx server defines an *upstream pool* of backend proxy nodes:

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

Each HTTPS vhost then proxies authenticated traffic into the backend pool.
If the site uses OAuth2, its configuration includes an authentication gate:

```nginx
location = /oauth2/auth {
    proxy_pass http://127.0.0.1:4180; 
    proxy_set_header Host $http_host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_pass_request_body off;
    proxy_set_header Content-Length "";
}

location / {
    auth_request /oauth2/auth;
    error_page 401 = /oauth2/sign_in;

    proxy_pass http://backend;
}
```

The OAuth2 Proxy service running locally on the frontend authenticates the user via **Microsoft Entra ID** before backend servers ever see the request.

---

## 🗄️ Backend Server Configuration

Backend Nginx servers are intentionally simple.
They act only as reverse proxies to the internal application servers and do **not** terminate SSL or run OAuth2 logic:

```nginx
location / {
    proxy_pass http://192.168.2.186:80;
}
```

Frontend nodes perform all heavy lifting — SSL, authentication, routing — while backend nodes focus purely on forwarding.

---

## 🔄 Full Request Flow (OAuth2 + Reverse Proxy)

### ASCII Architecture Diagram

```
                           ┌──────────────────────────────┐
                           │        Internet Client       │
                           └───────────────┬──────────────┘
                                           │ HTTPS
                                           ▼
                        ┌──────────────────────────────────────┐
                        │    Frontend Nginx Reverse Proxy      │
                        │ (SSL termination + OAuth2 enforcement│
                        │       + routing to backend)          │
                        └──────────────────────────┬───────────┘
                 OAuth2 Sites Only                 │ 
                         │                         │
                         ▼                         │
                ┌────────────────────────────┐     │
                │         OAuth2 Proxy       │     │  
                │ (Microsoft Entra ID OIDC)  │     │ Normal Sites
                └───────────────┬────────────┘     │
                                │ Token Issuance   │
                                ▼                  │
                     ┌────────────────────────┐    │
                     │   Microsoft Entra ID   │    │
                     └────────────────────────┘    │
                         │                         ▼
                         ▼  Authenticated, Header-Injected Traffic
       ┌────────────────────────────────────────────────────────────────┐
       │                 Backend Reverse-Proxy Pool (HA)                │
       │   upstream backend { rproxy-1; rproxy-2 backup; }              │
       └───────┬────────────────────────────────────────────────────────┘
               │
     ┌─────────┴───────────┐
     │                     │
┌────────────┐      ┌───────────┐
│ rproxy-1   │      │ rproxy-2  │ (Backup)
└─────┬──────┘      └─────┬─────┘
      │                   │
      ▼                   ▼
┌───────────────┐    ┌──────────────┐
│ App Server(s) │    │ App Server(s)│
└───────────────┘    └──────────────┘
```

---

## ❓ Why This Design

This architecture is intentionally layered to balance security, reliability, and maintainability.

### **1. Clear Separation of Responsibilities**

* **[Frontend Nginx](reverse-proxy#%ef%b8%8f-frontend-server-configuration.md)**

  * Terminates SSL
  * Performs OAuth2 authentication
  * Controls routing
* **[OAuth2 Proxy](oauth2_proxy.md)**

  * Handles identity logic
  * Integrates with Microsoft Entra ID
  * Injects identity headers
* **[Backend Nginx](reverse-proxy#%ef%b8%8f-backend-server-configuration.md)**

  * Only performs simple reverse proxy duties

This avoids complexity on backend nodes and makes identity management uniform.

---

### **2. Centralized Authentication**

Only the frontend server runs OAuth2 Proxy instances, ensuring:

* No duplication of identity configuration
* Unified logging
* Consistent session handling
* Predictable behavior across all OAuth2-protected services

---

### **3. Minimal Exposure of Internal Network**

Frontend handles all public traffic, so backend servers:

* Need not expose SSL or OAuth2
* Are unreachable from the public internet
* Can run lighter configurations with fewer security concerns

---

### **4. Simplified Automation**

With configuration templates and per-domain OAuth2 Proxy services, the system is fully idempotent:

* Add a domain → Service and config generated
* Remove a domain → Service and config removed
* Backend nodes remain unchanged

---

## 🟩 High Availability (HA) Characteristics

The architecture supports HA using lightweight but effective mechanisms:

### **Backend Redundancy**

The upstream block:

```
upstream backend {
  server rproxy-1:80 max_fails=3 fail_timeout=5s;
  server rproxy-2:80 backup;
}
```

achieves:

* **Automatic failover**
  If rproxy-1 fails 3 times in 5 seconds, traffic moves to rproxy-2
* **Active/Backup mode** (most efficient for small homelabs)

---

### **Stateless OAuth2 Authentication**

Because OAuth2 Proxy uses **cookie-based sessions**, the frontend can be scaled:

* Multiple frontends can be added later
* No shared DB or cache is required
* Entra ID acts as the authoritative identity backend

---

### **Frontend as the Control Plane**

The frontend is the *authoritative router* and *authentication gatekeeper*.

Backend nodes never need to know:

* Who the user is
* Whether they're authenticated
* Whether they’re allowed

The frontend injects all required headers:

* `X-Auth-Request-User`
* `X-Auth-Request-Email`
* `Authorization: Bearer <token>`

