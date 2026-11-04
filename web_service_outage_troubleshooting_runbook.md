---
title: "Web Service Outage Troubleshooting Runbook"
---

# 🌐 Web Service Outage Troubleshooting Runbook

This runbook provides **step-by-step instructions to diagnose and resolve web service outages** in the Home Lab. Traffic reaches the stack via one of two entry paths — **External** through Cloudflare, or **Internal** through Pi-hole DNS — and both paths converge at rproxy-0. OAuth2 identity verification via Azure Entra ID is handled at rproxy-0 and may or may not be enabled depending on the service.

> ⚡ Important: Start with **0️⃣ Quick Triage**. A stopped backend service or a powered-off VM is the most common cause of an outage, and it shows up as a **502 Bad Gateway** from Cloudflare or nginx — which looks like a proxy or Cloudflare problem but isn't.

---

## 🗺️ End-to-End Traffic Flow

{% raw %}
```
  EXTERNAL PATH                           INTERNAL PATH
  [ Browser / Client ]                    [ Browser / Client ]
          |                                       |
          | HTTPS (443)                           | HTTPS (443)
          v                                       v
  [ Cloudflare ]                          [ Pi-hole DNS ]
  WAF · DDoS · TLS Edge · CDN             192.168.20.253 (primary)
  Anycast → Nearest PoP                           |
          |                                       |
          | Origin Pull (Proxied HTTPS)           | Resolved A record → rproxy-0
          |                                       |
          +———————————————————+———————————————————+
                              |
                              v
                       [ rproxy-0 ]
                 nginx · upstream block
                 Static IP · entry proxy
                              |
                 ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
                 (optional) OAuth2 Proxy
                 Azure Entra ID — identity
                 verification before upstream
                 ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
                              |
                    ┌─────────┴─────────┐
                    v                   v
             [ rproxy-1 ]         [ rproxy-2 ]
             App Reverse Proxy    App Reverse Proxy
                    └─────────┬─────────┘
                              |
                              v
                 [ Backend Service ]
                 [ backend-01 :8080 ] 
```
{% endraw %}

---

## 0️⃣ Quick Triage — Is the Backend VM and Service Up?

> Do this first, regardless of entry path. If the backend is down, every proxy tier in front of it will return **502 Bad Gateway** (or Cloudflare **502 / 521**), and the Cloudflare, Pi-hole, and rproxy checks below will all look healthy.

Run from the Ansible control node, using the inventory the service is deployed from (example: Lidarr on `lidarr-0`).

### Step 1 — Is the VM up?

{% raw %}
```shell
ansible -i inventory/services/inventory.ini lidarr -m ping
```
{% endraw %}

* **SUCCESS / pong** → VM is up and reachable. Go to Step 2.
* **UNREACHABLE** → The VM is down, hung, or has lost networking. Check it in Proxmox:

{% raw %}
```shell
ssh <pve-node>
sudo qm list | grep -i lidarr
# or across the whole cluster:
sudo pvesh get /cluster/resources --type vm --output-format text | grep -i lidarr
```
{% endraw %}

* **stopped** → Start it (`sudo qm start <vmid>`), wait for it to boot, then repeat Step 1.
* **running but unreachable** → Open the VM console in the Proxmox UI and check for a hung boot, a full disk, or a lost network config.

### Step 2 — Is the service running on the VM?

Docker-based service:

{% raw %}
```shell
ansible -i inventory/services/inventory.ini lidarr -b -a "docker ps -a"
```
{% endraw %}

* Container **Exited** or **Restarting** → Check logs with `docker logs --tail 100 <container>`, then restart the container or re-run the service's deploy playbook.

Native (systemd) service:

{% raw %}
```shell
ansible -i inventory/services/inventory.ini lidarr -b -a "systemctl status <service> --no-pager"
```
{% endraw %}

### Step 3 — Does the service answer locally?

{% raw %}
```shell
ansible -i inventory/services/inventory.ini lidarr -a "curl -Is http://localhost:8686"
```
{% endraw %}

* **Any HTTP response** → The backend is serving. Continue with the entry-path sections below.
* **Connection refused / timeout** → The process is up but not listening. Check the application logs and resource usage (see 5️⃣).

> ⚡ Note: If the VM and service are both healthy, move on to **1️⃣ External** or **2️⃣ Internal** based on where the client is coming from.

---

## 1️⃣ External Path — Check Cloudflare

> Follow this section if the client is coming from the **internet** and traffic enters via Cloudflare.

Confirm the site is reachable from the public internet:

{% raw %}
```shell
curl -Isk https://your-domain.example.com | head -5
```
{% endraw %}

* **HTTP 200 / 301 / 302** → Edge is responding. Skip to step 5.
* **HTTP 502** → Usually the backend service or its VM is down. Re-check **0️⃣ Quick Triage**, then rproxy-0 (3️⃣) and rproxy-1/2 (4️⃣).
* **HTTP 521 / 522 / 523 / 524** → Cloudflare cannot reach the origin. Work through this section.
* **Timeout or DNS NXDOMAIN** → Likely a Cloudflare DNS misconfiguration.

### Cloudflare Dashboard Checks

1. Log in to **dash.cloudflare.com** and open your zone.
2. Confirm the DNS A record for your domain is **proxied** (orange cloud icon).
3. Check **Analytics & Logs → Traffic** for a spike in 5xx errors.
4. Check **Security → WAF** for any rules that may be blocking origin traffic.
5. Confirm SSL/TLS mode is set to **Full (Strict)**.
6. Visit **cloudflarestatus.com** to rule out a platform-wide incident.

> ⚡ Important: A grey-cloud (DNS-only) record means traffic bypasses Cloudflare entirely. Verify proxy status before anything else.

---

## 2️⃣ Internal Path — Check Pi-hole DNS

> Follow this section if the client is on the **internal network** and traffic is routed via Pi-hole DNS resolution.

Verify that Pi-hole resolves the domain to the rproxy-0 address:

{% raw %}
```shell
dig lidarr.refol.us @192.168.20.253
```
{% endraw %}

Expected: The A record should point to the **rproxy-0 IP address**.

### Pi-hole Service Health

{% raw %}
```shell
ssh <pi-hole-host>
sudo systemctl status pihole-FTL
sudo systemctl status lighttpd
pihole -t
```
{% endraw %}

### Upstream Resolver Reachability

Perform the following from proxy-0.

{% raw %}
```shell
curl http://192.168.20.211
curl http://192.168.20.212
```
{% endraw %}

* If **192.168.20.211** is unreachable → check router/firewall rules. Pi-hole will fall back to **192.168.20.212** automatically.
* If **both** are unreachable → check the upstream network segment and routing.

### Flush Pi-hole DNS Cache

{% raw %}
```shell
pihole restartdns
```
{% endraw %}

> ⚡ Important: Always verify both upstream IPs individually. A silent failure on .211 with no failover to .212 is a common cause of intermittent internal DNS outages.

---

## 3️⃣ Shared Path — rproxy-0 Entry Proxy

> Both the External and Internal paths converge here. Follow this section regardless of entry path.

Check the nginx service status and validate the running configuration:

{% raw %}
```shell
ssh rproxy-0
sudo systemctl status nginx
sudo nginx -t
```
{% endraw %}

Review recent errors:

{% raw %}
```shell
sudo tail -50 /var/log/nginx/error.log
sudo tail -50 /var/log/nginx/access.log | grep " 5[0-9][0-9] "
```
{% endraw %}

Inspect the upstream block to confirm rproxy-1 and rproxy-2 are correctly defined:

{% raw %}
```shell
grep -A 20 "upstream" /etc/nginx/nginx.conf
# or if configs are split:
grep -rA 20 "upstream" /etc/nginx/conf.d/
```
{% endraw %}

If a config change is needed, always test before reloading:

{% raw %}
```shell
sudo nginx -t && sudo systemctl reload nginx
```
{% endraw %}

### OAuth2 Proxy — Azure Entra ID (Optional)

> ⚡ Note: A **500 Internal Server Error** shown before the OAuth2 sign-on screen in the browser typically indicates that the OAuth2 service for the application is down.

rproxy-0 may be configured to run an OAuth2 proxy in front of upstream services. This is **not enabled for every service** — confirm whether the affected service uses it before investigating.

If OAuth2 is enabled for the service, check the proxy process and logs:

{% raw %}
```shell
sudo systemctl status oauth2-proxy_lidarr.refol.us.service
sudo journalctl -u oauth2-proxy_lidarr.refol.us.service -n 100 --no-pager
```
{% endraw %}

> ⚡ Note: each web service that is configured using its own oauth2 service.

> ⚡ Important: An expired client secret causes a hard auth failure with no useful browser-side error. Check secret expiry first when redirect loops are observed.

> ⚡ Note: A **500 Internal Server Error** shown in the browser after successfully authenticating in Azure typically indicates that there is an issue with the Entra ID service for the application is down. Journalctl will also show the message "Error redeeming code during OAuth2 callback: token exchange failed" when tailing the particular service journal entries.

Confirm the Entra ID OIDC metadata endpoint is reachable from rproxy-0:

{% raw %}
```shell
curl -s https://login.microsoftonline.com/<tenant-id>/v2.0/.well-known/openid-configuration \
  | python3 -m json.tool | head -20
```
{% endraw %}

Check the App Registration in **portal.azure.com → Microsoft Entra ID → Manage → App Registrations → All applications**:

1. Confirm **Redirect URIs** match your domain exactly — trailing slashes and casing matter.
2. Check **Certificates & Secrets** for any expired client secrets.
3. Navigate to **Security → Conditional Access → Policies** and look for any recently modified policy targeting the app or its users.

> ⚡ Important: An expired client secret causes a hard auth failure with no useful browser-side error. Check secret expiry first when redirect loops are observed.

---

## 4️⃣ Shared Path — rproxy-1 / rproxy-2 Application Proxies

Check the nginx service status and recent error logs on both nodes:

{% raw %}
```shell
for host in rproxy-1 rproxy-2; do
  echo "=== $host ===";
  ssh $host "sudo systemctl status nginx; sudo tail -20 /var/log/nginx/error.log";
done
```
{% endraw %}

Test that each proxy node can reach the backend pool:

{% raw %}
```shell
# Run from rproxy-1 or rproxy-2
curl -Isk http://192.168.20.151:8686
```
{% endraw %}

> ⚡ Note: `connect() failed (111: Connection refused)` or `upstream timed out` in the error log means the backend is down or unreachable — go back to **0️⃣ Quick Triage**.

> ⚡ Important: If one proxy node is healthy and the other is not, rproxy-0's upstream block may still be sending traffic to the failed node. Check that nginx upstream health checks are active and that the failed node's weight has not been manually set to 0.

---

## 5️⃣ Shared Path — Backend Services

> The basic VM and service checks are in **0️⃣ Quick Triage**. Use this section for deeper investigation on the backend host.

If the application is deployed using Docker, check if the container is running:

{% raw %}
```shell
sudo docker ps -a
sudo docker logs --tail 100 <container>
```
{% endraw %}

If the application is deployed using a native service, check if the service is running:

{% raw %}
```shell
sudo systemctl status <service> --no-pager
sudo journalctl -u <service> -n 100 --no-pager
```
{% endraw %}

Check the application health endpoint directly:

{% raw %}
```shell
curl -s http://localhost:8686
```
{% endraw %}

Check for resource exhaustion:

{% raw %}
```shell
uptime
free -h
df -h
```
{% endraw %}

## 6️⃣ Verify Service Restoration

After any fix is applied, confirm end-to-end functionality before closing the incident:

1. Open **your-domain.example.com** in a browser from both an **external** device and an **internal** host.
2. If OAuth2 is enabled for the service, navigate to a **protected page** and confirm the Entra ID login flow completes successfully.
3. Confirm **no 5xx errors** appear in Cloudflare Analytics → Traffic (external path).
4. Confirm **Pi-hole query log** shows clean resolution for your domain (internal path).
5. Confirm **rproxy-0 nginx access log** shows 200s flowing through to the upstream nodes.

{% raw %}
```shell
# External path — final check
curl -Isk https://lidarr.refol.us | head -5

# Internal path — final DNS check
dig lidarr.refol.us @192.168.20.253

# Confirm upstream traffic on rproxy-0
sudo tail -20 /var/log/nginx/access.log
```
{% endraw %}

> ⚡ Important: Validate both entry paths before closing. A fix that restores the external path does not guarantee the internal path is healthy, and vice versa.

---

### ✅ Notes

* Always start on the Ansible control node so remediation commands run in the correct environment.
* **Run 0️⃣ Quick Triage first** — confirm the backend VM is up and the service is running before investigating Cloudflare, Pi-hole, or the proxies. A down backend is the most common cause of a 502.
* Use the traffic flow diagram at the top of this page to identify which path is affected before starting.
* After triage, work **outside-in on each path**: Cloudflare → rproxy-0 for external; Pi-hole → rproxy-0 for internal.
* Both paths share the rproxy-0 → rproxy-1/2 → backend tier — a failure there affects all clients regardless of entry path.
* OAuth2 / Entra ID authentication is **optional per service** and runs at rproxy-0. Confirm whether it is enabled before investigating auth issues.
* Pi-hole IP **192.168.20.253** must be reachable.
* Always run `sudo nginx -t` before any `systemctl reload nginx` — a bad config will take the proxy down.
* Use `--check --diff` on any Ansible playbook before applying changes during a live incident.
* Log every action and timestamp in the incident ticket as you go — the post-mortem depends on it.
