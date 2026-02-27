---
title: "shellcheck sourceetc/cloudflare/secrets.conf"
---

## ⚙️ Automated Cloudflare DNS Updates

Cloudflare acts as the public ingress layer for the homelab, so the WAN IP must remain accurate in DNS. Because residential ISPs periodically rotate IP addresses, a lightweight DDNS script runs on the homelab to automatically update the Cloudflare A record whenever the WAN IP changes. The script uses [Cloudflare's API](https://developers.cloudflare.com/api/resources/dns/subresources/records/methods/update/).

This implementation keeps **all secrets in a separate file**, ensuring credentials never appear in scripts, logs, or version control.

### 📁 Secrets File

Create a secure file containing your Cloudflare credentials:

{% raw %}
```
/etc/cloudflare/secrets.conf
```
{% endraw %}

Example:

{% raw %}
```
CF_API_TOKEN="your_api_token"
ZONE_ID="your_zone_id"
RECORD_ID="your_record_id"
RECORD_NAME="refol.us"
```
{% endraw %}

Lock down permissions:

{% raw %}
```bash
chmod 600 /etc/cloudflare/secrets.conf
```
{% endraw %}

### 🧩 DDNS Update Script

This script loads the secrets file, checks the current public IP, compares it to the value stored in Cloudflare, and updates the DNS record only when necessary.

{% raw %}
```bash
#!/usr/bin/env bash

SECRET_FILE="/etc/cloudflare/secrets.conf"

if [ ! -f "$SECRET_FILE" ]; then
    echo "Missing secrets file: $SECRET_FILE"
    exit 1
fi

# shellcheck source=/etc/cloudflare/secrets.conf
source "$SECRET_FILE"

REQUIRED_VARS=(CF_API_TOKEN ZONE_ID RECORD_ID RECORD_NAME)
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Missing required variable: $var"
        exit 1
    fi
done

CURRENT_IP=$(curl -s https://api.ipify.org)

CF_DATA=$(curl -s -X GET \
  "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records/$RECORD_ID" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json")

CF_IP=$(echo "$CF_DATA" | jq -r '.result.content')
CF_PROXIED=$(echo "$CF_DATA" | jq -r '.result.proxied')

if [ "$CURRENT_IP" = "$CF_IP" ]; then
    echo "IP unchanged ($CURRENT_IP). No update needed."
    exit 0
fi

echo "Updating Cloudflare DNS: $CF_IP → $CURRENT_IP"

UPDATE=$(curl -s -X PUT \
  "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records/$RECORD_ID" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data "{\"type\":\"A\",\"name\":\"$RECORD_NAME\",\"content\":\"$CURRENT_IP\",\"ttl\":120,\"proxied\":$CF_PROXIED}")

echo "$UPDATE"
```
{% endraw %}

### ⏱️ Scheduling

Add a cron entry to run the script periodically:

{% raw %}
```bash
*/5 * * * * /usr/local/bin/cloudflare-ddns.sh >/dev/null 2>&1
```
{% endraw %}

This ensures Cloudflare always reflects the current WAN IP without exposing the homelab directly.
