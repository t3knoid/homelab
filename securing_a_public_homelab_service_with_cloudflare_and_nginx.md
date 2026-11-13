---
title: "Securing a Public Homelab Service with Cloudflare and Nginx"
---

# 🔐 Securing a Public Homelab Service with Cloudflare and Nginx

This how-to article covers exposing a homelab web service to the internet without exposing all of it. Cloudflare's free plan protects the edge, and the frontend Nginx reverse proxy decides which paths the internet can reach.

It applies to any service that needs a public page but keeps admin functions on the LAN. ROSIE, the homelab's self-hosted AI assistant, was the first service published this way (See [Building ROSIE](building_rosie.md)).

Examples on this page use `app.refol.us` as the site name. Replace it, the paths and the limits with the service's own.

---

## 🧭 **1. The Problem**

A typical homelab site passes every request straight to the app. The site's server block allows only the LAN subnets and Cloudflare's IP ranges, then denies everything else. That stops anyone from going around Cloudflare.

But every internet visitor arrives from a Cloudflare IP. To Nginx, "allow Cloudflare" means "allow the whole internet." That leaves two common gaps:

- **Admin endpoints are reachable by anyone.** Many self-hosted apps expose upload, sync, settings or API docs endpoints with weak or no authentication.
- **Expensive endpoints can be abused.** A search, AI or report endpoint that takes seconds of CPU or GPU per request can be tied up by a single script.

The fix is layered. Cloudflare filters at the edge, and Nginx makes only the pages the public needs reachable and rate-limits the expensive ones per visitor.

---

## 🏗️ **2. Architecture**

{% raw %}
```
          Internet visitor
                 │
                 ▼
┌──────────────────────────────────┐
│ Cloudflare (free plan)           │
│  • Proxied DNS (hides WAN IP)    │
│  • TLS, DDoS protection          │
│  • Turnstile, rate limiting rule │
└──────────────────────────────────┘
                 │  Cloudflare IPs only
                 ▼
┌──────────────────────────────────┐
│ Frontend Nginx (DMZ)             │
│  • Cloudflare + LAN allowlist    │
│  • Public path allowlist         │
│  • Per-visitor rate limit        │
└──────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│ Backend Nginx pool → app         │
│  • Turnstile token check         │
└──────────────────────────────────┘
```
{% endraw %}

Each layer does one job:

| Layer | Job |
| --- | --- |
| Cloudflare | Hides the WAN IP, terminates public TLS, absorbs floods before they reach home bandwidth |
| Frontend Nginx | Decides which paths the internet can reach, rate-limits expensive endpoints per real visitor |
| Backend Nginx | Accepts traffic only from the frontend proxy, never from the internet or other hosts |
| VLAN ACLs | Block any path to the backend and the services that doesn't come from the frontend proxy |
| App | Verifies the Turnstile token so scripts can't use public forms |

See [Homelab Network Architecture and Traffic Flows](homelab_network_architecture_and_traffic_flows.md) for where each piece sits on the network.

### **Double reverse proxy and VLAN isolation**

The Cloudflare and Nginx controls in this how-to work best on top of a double reverse proxy, as documented in [Reverse-Proxy](reverse-proxy.md). A frontend proxy faces the internet, and a separate backend proxy faces the services. If the frontend is ever misconfigured or compromised, the services still sit behind a second proxy and a network boundary.

- **Frontend proxy.** Sits on an internet-facing VLAN (the DMZ) and only accepts traffic from Cloudflare. It terminates TLS, applies the path allowlist and rate limits, then forwards to the backend.
- **Backend proxy.** Sits on an internal VLAN and only accepts traffic from the frontend proxy. It never accepts traffic from the internet, from Cloudflare, or from any other host.
- **VLAN ACLs.** The gateway enforces the same rule at the network layer. Only the frontend proxy's address, on the DMZ VLAN, may reach the backend proxy. Everything else from the DMZ is denied.

In this homelab, the flow looks like this:

{% raw %}
```
Internet → Cloudflare → Frontend proxy (DMZ VLAN) → Backend proxy (internal VLAN) → Services
                         accepts Cloudflare only     accepts frontend proxy only
```
{% endraw %}

An example of the gateway ACL rules:

| Source | Destination | Port | Action |
| --- | --- | --- | --- |
| Frontend proxy (DMZ VLAN) | Backend proxy (internal VLAN) | 80 | Allow |
| DMZ VLAN (any other host) | Internal VLANs | any | Deny |
| Internet | Backend proxy | any | Deny |

The backend proxy can enforce the same rule in Nginx, so a gap in the ACLs doesn't open it up. In each backend server block, replace the address with the frontend proxy's:

{% raw %}
```
allow 192.0.2.10;    # frontend proxy only
deny  all;
```
{% endraw %}

See [VLAN Architecture and Segmentation](vlan_architecture_and_segmentation.md), [DMZ Network Design and Implementation](dmz_network_design_and_implementation.md) and [Gateway VLAN ACL Rules](gateway_vlan_acl_rules.md) for how the VLANs and rules are set up.

---

## ☁️ **3. Cloudflare Free Features**

The base Cloudflare setup (proxied DNS, Full (Strict) TLS, router firewall) is documented on the [Cloudflare](cloudflare.md) page. This how-to adds two free features on top.

| Feature | What it does |
| --- | --- |
| Proxied DNS (orange cloud) | Visitors only ever see Cloudflare's IPs |
| Universal SSL + Full (Strict) | Public TLS at the edge, validated against the origin certificate |
| DDoS protection | Absorbs volumetric attacks before they reach the WAN link |
| Turnstile | Free CAPTCHA alternative. The page gets a token, and the app verifies it before acting |
| Rate limiting rule | The free plan includes one rule, matched on the URI path and counted per IP |

### **Turnstile**

Turnstile needs support in the app: the page renders the widget, and the server verifies the token.

1. In the Cloudflare dashboard, open **Turnstile** and add a widget for the site's hostname.
2. Choose the **Managed** widget mode.
3. Give the site key to the page and the secret key to the app.
4. The app checks each token with Cloudflare's `siteverify` endpoint and rejects requests that fail.

If the app doesn't support Turnstile, skip it. The Nginx path allowlist and rate limits still apply.

### **Rate limiting rule**

On the free plan, a rate limiting rule matches on the URI path, counts per IP, and uses a fixed 10-second period and 10-second block.

1. Go to **Security → WAF → Rate limiting rules** and create a rule.
2. Expression: `(http.request.uri.path eq "/api/submit")`, using the site's most expensive public endpoint.
3. Characteristics: **IP**.
4. Requests: a number that a real user won't hit in 10 seconds, for example **3**.
5. Action: **Block**.

This stops a flood at Cloudflare. The Nginx limit below stays as the backstop, because a 10-second window can't express a limit like "3 a minute."

---

## 🌐 **4. Public Path Allowlist**

Start by listing what the public page actually calls. The browser's developer tools (Network tab) show every request the page makes. Everything not on that list stays LAN-only.

Because this is an allowlist, any endpoint the app adds later stays LAN-only until it's opened here.

| Path | Method | Who can reach it | Limits |
| --- | --- | --- | --- |
| `/` (public page) | GET | Everyone, through Cloudflare | |
| `/static/` | GET | Everyone, through Cloudflare | |
| `/api/submit` (expensive endpoint) | POST | Everyone, through Cloudflare | 3 a minute per visitor (burst 2), 1 in progress, 16 KB body, Turnstile in the app |
| Everything else: admin, upload, sync, API docs | any | LAN subnets only | 10 MB body for uploads |

A public path returns 403 for any method other than the one listed.

---

## 🧩 **5. Where This Fits in the Reverse Proxy Deployment**

Publishing the site itself follows the [Configure An Inventory Host Web Service For A Reverse Proxy](configure_an_inventory_host_web_service_for_a_reverse_proxy.md) runbook. Its certificate follows the [Request Web Certificates Runbook](request_web_certificates_runbook.md).

This how-to adds a layer on top of that site: the path allowlist and rate limits in the next section.

> ⚠️ **Note:** The site files on the proxy are managed by the deployment. Hand edits are overwritten on the next run, so make these changes part of the deployment.

---

## ⚙️ **6. Nginx Configuration**

The configuration lives on the frontend Nginx server. Three snippets go in `/data/nginx/snippets/`, and the site file `/data/nginx/sites-enabled/app.refol.us.conf` includes them.

> 📁 **Note:** These paths are examples from this homelab, which keeps Nginx's files under `/data/nginx/`. A stock install usually uses `/etc/nginx/` instead (for example `/etc/nginx/snippets/` and `/etc/nginx/sites-enabled/`, or `/etc/nginx/conf.d/`). Adjust them to match your Nginx install, here and in every `include` line below.

### **Shared proxy settings: `app-proxy.conf`**

A location that sets any `proxy_set_header` loses the inherited ones, so every location includes this file. Copy the settings from the site's existing `location /` block.

{% raw %}
```
proxy_pass http://backend;
proxy_set_header Host              $http_host;
proxy_set_header X-Real-IP         $remote_addr;
proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
proxy_set_header X-Forwarded-Host  app.refol.us;
proxy_http_version 1.1;
proxy_set_header Upgrade    $http_upgrade;
proxy_set_header Connection $http_connection;
proxy_connect_timeout 90;
proxy_send_timeout    90;
proxy_read_timeout    90;
```
{% endraw %}

### **Rate-limit zones: `app-limits.conf`**

These belong in Nginx's `http` context, so this file is included above the `server` block. Cloudflare sends the visitor's real IP in `CF-Connecting-IP`. LAN clients don't send it, so they fall back to their own address. Trusting that header is safe only because the server block admits nothing but Cloudflare and the LAN.

{% raw %}
```
map $http_cf_connecting_ip $app_client {
    ""      $binary_remote_addr;
    default $http_cf_connecting_ip;
}
limit_req_zone  $app_client zone=app_submit:10m rate=3r/m;
limit_conn_zone $app_client zone=app_conn:10m;
```
{% endraw %}

Zone names must be unique across all sites on the proxy, so prefix them with the site name.

### **Locations: `app-locations.conf`**

This replaces the site's original `location /` block.

{% raw %}
```
# ---- Public: the page and the calls it makes ----
location = / {
    limit_except GET { deny all; }
    include /data/nginx/snippets/app-proxy.conf;
}

location /static/ {
    limit_except GET { deny all; }
    include /data/nginx/snippets/app-proxy.conf;
}

location = /api/submit {
    limit_except POST { deny all; }
    limit_req  zone=app_submit burst=2 nodelay;
    limit_conn app_conn 1;
    limit_req_status  429;
    limit_conn_status 429;
    client_max_body_size 16k;
    include /data/nginx/snippets/app-proxy.conf;
}

# ---- Everything else: LAN only ----
location / {
    allow 10.0.0.0/24;
    allow 192.168.2.0/24;
    allow 192.168.10.0/24;
    allow 192.168.20.0/24;
    deny all;

    client_max_body_size 10m;
    include /data/nginx/snippets/app-proxy.conf;
}
```
{% endraw %}

If the page expects JSON errors, add a named location that returns a JSON 429 body and point `error_page 429` at it.

### **Site file: `app.refol.us.conf`**

Two changes:

1. Above the `server {` line, add `include /data/nginx/snippets/app-limits.conf;`.
2. Replace the whole `location / { ... }` block with `include /data/nginx/snippets/app-locations.conf;`. Keep the existing `allow`, Cloudflare `include` and `deny all` lines above it.

The server-level rules stay as they are: Cloudflare and the LAN subnets in, everyone else denied. TLS settings and certificates are unchanged.

### **Keeping the Cloudflare ranges current**

The server block's Cloudflare allowlist comes from `cloudflare-allow.conf` and `cloudflare-allow-ipv6.conf`, written by the reverse proxy deployment. Cloudflare changes its ranges occasionally, and a stale list starts returning 403 to real visitors. Compare the files against [cloudflare.com/ips](https://www.cloudflare.com/ips/) periodically, and redeploy when they change.

Test and reload after any change:

{% raw %}
```
sudo nginx -t && sudo systemctl reload nginx
```
{% endraw %}

`nginx -t` needs root because it reads the TLS certificates under `/data/certs`.

---

## ✅ **7. Verification**

Test from outside the network, for example from a phone on cellular data. From the LAN every path is allowed, so a LAN test proves nothing.

{% raw %}
```
curl -s -o /dev/null -w '%{http_code}\n' https://app.refol.us/                 # 200
curl -s -o /dev/null -w '%{http_code}\n' https://app.refol.us/static/app.css   # 200
curl -s -o /dev/null -w '%{http_code}\n' https://app.refol.us/admin            # 403
curl -s -o /dev/null -w '%{http_code}\n' https://app.refol.us/api/submit       # 403 (GET)
```
{% endraw %}

Then open the page and use it normally to confirm nothing it needs was left off the allowlist. A 403 in the browser's Network tab points to a missing path.

To check the Nginx rate limit, send a quick burst. The first three requests reach the app (and get 403 if it checks Turnstile). The rest get 429 from Nginx:

{% raw %}
```
for i in 1 2 3 4 5; do
  curl -s -o /dev/null -w '%{http_code}\n' -X POST https://app.refol.us/api/submit
done
# expect: three app responses, then 429 429
```
{% endraw %}

Cloudflare's rate limiting rule can block a burst first. Check **Security → Events** in the Cloudflare dashboard to see which layer stopped it.

---

## ↩️ **8. Rollback**

The quickest rollback is to redeploy the site without the changes, which restores the original site file.

In an emergency, on the frontend, put the original `location /` block back into the site's `.conf` file in place of the `include` line, remove the limits include, then:

{% raw %}
```
sudo nginx -t && sudo systemctl reload nginx
```
{% endraw %}

The Cloudflare rate limiting rule can be disabled from the dashboard without touching Nginx.

---

## 📝 **9. Notes**

- **Some links in the app may break for internet visitors.** Any button that calls a LAN-only endpoint returns 403 from outside. That's expected. The app may need to hide those buttons for public visitors.
- **Don't turn on Nginx's real-IP module for these sites.** With `set_real_ip_from` and `real_ip_header CF-Connecting-IP`, Nginx would check the visitor's IP against the allowlist instead of Cloudflare's, and every internet visitor would get a 403. The `$app_client` map gives the rate limit the real IP without changing the address the allowlist sees.
- **Turnstile and Nginx do different jobs.** Turnstile stops scripts from using public forms. Nginx's limits stop anyone from tying up the backend, even with requests Turnstile will reject. Keep both.
- **Sites behind OAuth2 don't need this.** A site that requires sign-in through [OAuth2 Proxy](oauth2_proxy.md) is already closed to anonymous visitors. This how-to is for pages that must stay open to the public.
- **429s show up in the proxy metrics.** See [Nginx Reverse Proxy Monitoring](nginx_reverse_proxy_monitoring.md) to watch for spikes.

---

## 🛠️ **10. How This Homelab Manages It**

Most of the pieces in this how-to are deployed with [Ansible](ansible.md) in this homelab. The rest are configured by hand in the Cloudflare dashboard or the Omada controller.

| Area | How it's managed | Page |
| --- | --- | --- |
| Site definition on the frontend and backend proxies | Ansible | [Configure An Inventory Host Web Service For A Reverse Proxy](configure_an_inventory_host_web_service_for_a_reverse_proxy\.md) |
| Cloudflare-only allowlist on the frontend proxy | Ansible | [Configure An Inventory Host Web Service For A Reverse Proxy](configure_an_inventory_host_web_service_for_a_reverse_proxy\.md) |
| TLS certificates | Ansible | [Request Web Certificates Runbook](request_web_certificates_runbook\.md) |
| Internal DNS (Pi-hole CNAME) | Ansible | [Ansible Pi-hole and DNS Management Runbook](ansible_pi-hole_and_dns_management_runbook\.md) |
| Reverse proxy metrics | Ansible | [Deploy nginx-prometheus-exporter to Reverse Proxy hosts](deploy_nginx-prometheus-exporter_to_reverse_proxy_hosts\.md) |
| Public DNS record | Cron script | [Automated Cloudflare DNS Updates](automated_cloudflare_dns_updates\.md) |
| SSL mode, Turnstile, rate limiting rule | Cloudflare dashboard, by hand | [Cloudflare](cloudflare.md) |
| VLANs and gateway ACLs | Omada controller, by hand | [VLAN Creation Procedure](vlan_creation_procedure\.md), [Gateway VLAN ACL Rules](gateway_vlan_acl_rules\.md) |
| Path allowlist and rate-limit snippets | Not automated yet | See gaps below |

### **Gaps**

- **Per-site snippets aren't in the Ansible deployment yet.** The site definitions in the reverse proxy runbook have no option for extra include files, so the snippets in section 6 are hand edits that the next deployment overwrites. The `rproxy` role needs an option for per-site includes, and the runbook needs a section on using it.

---

## 🔗 **Related Pages**

- [Configure An Inventory Host Web Service For A Reverse Proxy](configure_an_inventory_host_web_service_for_a_reverse_proxy.md)
- [Request Web Certificates Runbook](request_web_certificates_runbook.md)
- [Cloudflare](cloudflare.md)
- [Automated Cloudflare DNS Updates](automated_cloudflare_dns_updates.md)
- [Reverse-Proxy](reverse-proxy.md)
- [Reverse-Proxy with OAuth2 Integration](reverse-proxy_with_oauth2_integration.md)
- [OAuth2 Proxy](oauth2_proxy.md)
- [Homelab Network Architecture and Traffic Flows](homelab_network_architecture_and_traffic_flows.md)
- [VLAN Architecture and Segmentation](vlan_architecture_and_segmentation.md)
- [DMZ Network Design and Implementation](dmz_network_design_and_implementation.md)
- [Gateway VLAN ACL Rules](gateway_vlan_acl_rules.md)
- [Nginx Reverse Proxy Monitoring](nginx_reverse_proxy_monitoring.md)