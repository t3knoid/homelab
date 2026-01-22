---
title: "OAuth2 Proxy"
---

# 🔐 OAuth2 Proxy

**OAuth2 Proxy** is an open‑source authentication and authorization gateway designed to sit in front of applications and enforce identity verification using modern OAuth2 and OIDC providers. It acts as a lightweight security layer that handles login redirects, token validation, session management, and identity header injection—allowing upstream services to remain simple and authentication‑agnostic.

In the homelab environment, OAuth2 Proxy integrates tightly with **[Microsoft Entra ID](microsoft_entra_id.md)** and the Nginx reverse‑proxy layer to provide consistent, centralized Single Sign‑On (SSO) across internal applications.

🔗 **Official Documentation**
 
For full upstream reference material, see:

- **GitHub Repository:**  
  `https://github.com/oauth2-proxy/oauth2-proxy`
- **OAuth2 Proxy Installation:**
  `https://oauth2-proxy.github.io/oauth2-proxy/installation`
- **Microsoft EntraID Integration:**  
  `https://oauth2-proxy.github.io/oauth2-proxy/configuration/providers/ms_entra_id`

---

---

## 🧭 Purpose in the Homelab

OAuth2 Proxy provides:

**Authentication Gateway for the Homelab Reverse‑Proxy Layer**

- **Centralized authentication** for all protected internal services  
- **OIDC login via Microsoft Entra ID**  
- **Identity header forwarding** (email, username, groups) to upstream apps  
- **Integration with Nginx** using `auth_request`  
- **Consistent SSO behavior** across Grafana, Proxmox, media apps, and admin tools  
- **Redis‑backed session storage** for scalable, stateless authentication across multiple reverse‑proxy nodes  

It does *not* replace Entra ID or Nginx. Instead, it acts as the **authentication engine** that Nginx delegates to.

---

## 🏗️ Architectural Role

{% raw %}
```
Client → Nginx Reverse Proxy → OAuth2 Proxy → Entra ID
                                   ↓
                              Upstream App
```
{% endraw %}

### Flow Summary
1. User requests a protected URL.  
2. Nginx calls `/oauth2/auth` to check authentication.  
3. OAuth2 Proxy redirects the user to Entra ID (`/oauth2/start`).  
4. After login, Entra ID returns the user to `/oauth2/callback`.  
5. OAuth2 Proxy validates the token and stores the session in Redis.  
6. Nginx forwards the request to the upstream service with identity attached.

---

## 🧩 Redis Session Storage

OAuth2 is configured to use **[Redis as the session backend](https://oauth2-proxy.github.io/oauth2-proxy/configuration/session_storage/)**. This provides:

- **Stateless authentication** — OAuth2 Proxy instances do not store sessions locally  
- **High availability** — sessions survive restarts and can be shared across nodes  
- **Improved performance** — Redis handles session lookups efficiently  
- **Consistent SSO** — users remain logged in even if the proxy restarts

### Why Redis Instead of Cookie Sessions?

While OAuth2 Proxy supports encrypted cookie‑based sessions, Redis is preferred because:

- Avoids cookie size limits
- Enables horizontal scaling
- Survives restarts
- Eliminates the “multiple cookies required” warning from Entra ID sessions

> [!NOTE]
> While using OAuth2 with EntraID, a warning in the OAuth2 logs stating, `Multiple 
> cookies are required for this session as it exceeds the 4kb cookie limit. Please use
> server side session storage (eg. Redis) instead` was shown. Using Redis with OAuth2
> removed this warning.

### Redis Configuration

Redis must be installed before OAuth2 Proxy. The **[`redis_setup`](https://github.com/t3knoid/ansible/tree/main/roles/redis_setup)** role handles installation, and `oauth2_proxy_setup` configures OAuth2 Proxy to use it with the following configuration settings.

- `--session-store-type=redis` - This is specified in the oauth2-proxy config file as `session_store_type = "redis"`
- `--redis-connection-url=redis://<host>:<port>` - redis_connection_url = "{{ oauth2_proxy_setup_redis_connection }}"

For a comprehensive documentation on OAuth2 proxy configuration settings,

👉 See: **[OAuth2 Proxy Configuration File Documentation](oauth2_proxy_configuration_file_documentation.md)**

---

## 📦 Installation & Management (Ansible Role)

The `oauth2_proxy_setup` role handles:

- Installing the OAuth2 Proxy binary  
- Creating the systemd service  
- Writing the configuration file  
- Injecting Entra ID client credentials  
- Managing cookie secrets and redirect URIs  
- Configuring Redis as the session backend  
- Ensuring consistent integration with the reverse‑proxy layer  

This role consumes outputs from the **[Entra ID OAuth2 Provisioning Ansible Role](entra_id_oauth2_provisioning_ansible_role.md)**, ensuring the OAuth2 Proxy instance is always aligned with the correct application registration. It also requires that Redis is pre-installed.

---

## ⚙️ Configuration Overview

### Key Endpoints
OAuth2 Proxy exposes:

- `/oauth2/start` – Begin login  
- `/oauth2/auth` – Nginx `auth_request` endpoint  
- `/oauth2/callback` – OIDC redirect target  

### Identity Headers Forwarded
Typical headers forwarded to upstream apps:

- `X-Auth-Request-Email`  
- `X-Auth-Request-User`  
- `X-Auth-Request-Groups`  

Your Nginx site definitions determine which headers are passed through.

### Session Handling with Redis

OAuth2 Proxy stores session data in Redis, including:

- User identity  
- Token metadata  
- Group claims  
- Session expiration  

This allows OAuth2 Proxy to remain stateless and restart‑safe.

---

## 🔑 Microsoft Entra ID Integration

OAuth2 Proxy uses Entra ID as its OIDC provider.  
Your provisioning role creates:

- Application registration  
- Client secret  
- Redirect URIs  
- Required API permissions (e.g., `User.Read`)  
- Optional group claim configuration  

OAuth2 Proxy consumes these values to authenticate users and extract identity information.

For a more detailed documentation on OAuth2 Proxy's integration with Entra ID,

👉 see: **[OAuth2 Proxy Integration with Entra ID](oauth2_proxy_integration_with_entra_id.md)**

---

## 🧩 Integration with Nginx Reverse Proxy

Each protected site defined in the `rproxy_setup_sites` inventory entry can enable OAuth2 authentication.

Nginx uses:

{% raw %}
```nginx
auth_request /oauth2/auth;
error_page 401 = /oauth2/start;
```
{% endraw %}

OAuth2 Proxy then validates the session (via Redis) and returns identity headers for Nginx to forward upstream.

This pattern ensures:

- Uniform authentication behavior  
- Minimal per‑site configuration  
- Centralized identity enforcement  
- Stateless scaling of the reverse‑proxy layer

For a more detailed documentation on OAuth2 integration with Nginx proxy,

👉 see: **[Reverse-Proxy with OAuth2 Integration](reverse-proxy_with_oauth2_integration.md)**

---

## 🔗 Related Pages

- **[Reverse-Proxy](reverse-proxy.md) Overview**  
- **[Reverse-Proxy with OAuth2 Integration](reverse-proxy_with_oauth2_integration.md)**
- **[Entra ID OAuth2 Provisioning Ansible Role](entra_id_oauth2_provisioning_ansible_role.md)**
- **Entra ID [Application Registration](application_registration.md)**  
- **[Contributor Guide Adding Entra ID OAuth2 Support for a Web Service](contributor_guide_adding_entra_id_oauth2_support_for_a_web_service.md)**