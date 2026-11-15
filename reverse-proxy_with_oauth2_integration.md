---
title: "️ Reverse-Proxy with OAuth2 Integration"
---

# 🛡️ Reverse-Proxy with OAuth2 Integration

This page explains how single sign-on is added to the [Reverse-Proxy](reverse-proxy.md) cluster: where OAuth2 Proxy runs, how a site is switched from public to protected, and what changes (and what doesn't) for the backends. It assumes the frontend/backend layout and failover described on the Reverse-Proxy page.

For the OAuth2 Proxy configuration file, the Entra ID sign-in sequence, and the full list of identity headers, see [OAuth2 Proxy Integration with Entra ID](oauth2_proxy_integration_with_entra_id.md).

---

## 📍 Where Authentication Lives

Authentication is handled entirely on the **frontend server**:

- Each protected domain has its own OAuth2 Proxy instance running on the frontend, bound to a loopback port (for example `127.0.0.1:4180`). It is never reachable from the network.
- Nginx asks that instance whether a request is allowed before proxying it.
- OAuth2 Proxy talks to **Microsoft Entra ID** for sign-in and token validation.

The backend nodes run no authentication software and hold no secrets. A request reaching them has already been checked.

---

## 🔀 Protected vs. Public Sites

Both kinds of site share the same frontend, upstream pool, and backends. The only difference is in the frontend virtual host.

{% raw %}
```
                        Frontend Nginx (DMZ)
                                │
              ┌─────────────────┴─────────────────┐
        Protected site                       Public site
              │                                   │
     auth_request /oauth2/auth                    │
              ▼                                   │
  OAuth2 Proxy (127.0.0.1:port) ◀──▶ Entra ID      │
              │                                   │
     202 → continue                               │
     401 → /oauth2/sign_in                        │
              │                                   │
              └─────────────────┬─────────────────┘
                                ▼
                upstream backend (rproxy-1 / rproxy-2)
                                ▼
                         Application server
```
{% endraw %}

A public site is a plain virtual host, as shown on the [Reverse-Proxy](reverse-proxy.md) page. A protected site adds an authentication gate.

---

## 🧱 Adding the Authentication Gate

To protect a site, two things are added to its frontend virtual host:

{% raw %}
```nginx
# 1. Internal endpoint Nginx calls to check the session
location = /oauth2/auth {
    proxy_pass http://127.0.0.1:4180;
    proxy_set_header Host $http_host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_pass_request_body off;
    proxy_set_header Content-Length "";
}

# 2. Gate on the application route
location / {
    auth_request /oauth2/auth;
    error_page 401 = /oauth2/sign_in;

    proxy_pass http://backend;
}
```
{% endraw %}

- `auth_request` sends a lightweight subrequest (headers only, no body) to OAuth2 Proxy for every incoming request.
- A `202` response lets the request continue to `http://backend`.
- A `401` response sends the user to `/oauth2/sign_in`, which starts the Entra ID login.
- `proxy_pass http://backend` is unchanged from a public site, so failover between rproxy-1 and rproxy-2 works the same way.

A complete production virtual host for `code.refol.us` is on [OAuth2 Proxy Integration with Entra ID](oauth2_proxy_integration_with_entra_id.md).

---

## 📨 What the Backends Receive

After a successful check, the frontend forwards the request with identity headers such as `X-Auth-Request-User`, `X-Auth-Request-Email`, and `Authorization: Bearer <token>`.

Backend nodes pass these through untouched. Applications that understand them can use the signed-in identity, and applications that don't can ignore them. Neither the backend proxies nor the applications need to implement OAuth2 or OIDC.

---

## 🔁 Sessions and Scaling

OAuth2 Proxy keeps sessions in **encrypted browser cookies**, not in a server-side store. As a result:

- No shared database or cache is needed for sessions.
- A second frontend could be added later and validate the same cookies, provided it uses the same cookie secret.
- Entra ID remains the single source of truth for identity.

---

## 🤖 Automation

OAuth2 Proxy instances and gate configuration are generated per domain from templates, so the process is idempotent:

- **Protect a domain:** an OAuth2 Proxy service and gated virtual host are created.
- **Remove protection:** the service and configuration are removed.
- **Backends:** never touched in either case.

---

## ❓ Why Authenticate at the Frontend?

- **One identity configuration.** Client IDs, secrets, and redirect URLs exist only on the frontend, not on every app or backend node.
- **Consistent behavior.** Every protected site uses the same login flow, session lifetime, and MFA policy from Entra ID.
- **Unified logging.** All sign-in and authorization decisions are recorded in one place.
- **Unauthenticated requests stop early.** They are rejected at the DMZ before reaching the internal VLAN.

---

## 🔗 Related Pages

- [Reverse-Proxy](reverse-proxy.md): cluster topology, Cloudflare edge, and failover
- [OAuth2 Proxy](oauth2_proxy.md): service overview
- [OAuth2 Proxy Integration with Entra ID](oauth2_proxy_integration_with_entra_id.md): config file, sign-in sequence, header reference
