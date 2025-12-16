# OAuth2 Proxy Architecture and Integration

This environment uses **OAuth2 Proxy** in combination with **Nginx** to enforce authentication across selected domains, with **Microsoft Entra ID (Azure Active Directory)** serving as the centralized identity provider. Authentication is handled through dedicated OAuth2 Proxy instances, each associated with its own domain and configuration file under `/etc/oauth2-proxy/`. This approach ensures clean separation of concerns, predictable automation, and domain-specific access control.

Nginx delegates authentication to OAuth2 Proxy via `auth_request`, while OAuth2 Proxy validates tokens issued by Entra ID and injects identity headers—such as `X-Auth-Request-User`, `X-Auth-Request-Email`, and `Authorization: Bearer <token>`—into upstream requests. Backend applications receive verified identity information without implementing OAuth2/OIDC logic.

> [!TIP]
> **For details on how OAuth2 Proxy is integrated with Nginx and the reverse-proxy cluster, 
> see [Reverse Proxy Frontend Server Configuration (with_OAuth2_Support)](reverse_proxy_frontend_server_configuration_(with_oauth2_support).md)**

---

## ⚙️ Nginx Configuration Example (`code.refol.us`)

```nginx
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name code.refol.us;

    ssl_certificate /data/certs/code.refol.us/fullchain.pem;
    ssl_certificate_key /data/certs/code.refol.us/privkey.pem;

    index index.html index.htm index.php;

    # Authentication entrypoint for oauth2-proxy
    location = /oauth2/auth {
        proxy_pass http://127.0.0.1:4180; 
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Content-Length "";
        proxy_pass_request_body off;
    }

    # Protected application routes
    location / {
        auth_request /oauth2/auth;
        error_page 401 = /oauth2/sign_in;

        proxy_pass http://backend;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host code.refol.us;

        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $http_connection;

        client_max_body_size 10m;
        client_body_buffer_size 128k;
        proxy_connect_timeout 90;
        proxy_send_timeout 90;
        proxy_read_timeout 90;
        proxy_request_buffering off;
    }

    # Security hardening
    location ~ /\.ht {
        deny all;
    }

    # ACME challenge for Let's Encrypt
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
        allow all;
    }
}

```

---

## 📁 OAuth2 Proxy Configuration (`code.refol.us`)

```ini
# /etc/oauth2-proxy/oauth2-proxy_code.refol.us.cfg

http_address = "127.0.0.1:4180"

provider = "azure"
client_id = "YOUR_AZURE_APP_CLIENT_ID"
client_secret = "YOUR_AZURE_APP_CLIENT_SECRET"
oidc_issuer_url = "https://login.microsoftonline.com/YOUR_TENANT_ID/v2.0"

redirect_url = "https://code.refol.us/oauth2/callback"

cookie_secret = "BASE64_32BYTE_RANDOM_STRING"
cookie_secure = true
cookie_http_only = true
cookie_expire = "168h"
cookie_refresh = "24h"

email_domains = ["refol.us"]

set_xauthrequest = true
pass_access_token = true
pass_authorization_header = true

request_logging = true
metrics_address = "127.0.0.1:9100"

```

---

## 🧩 Configuration Highlights

* **Per-domain proxy isolation**
  Each domain uses a dedicated OAuth2 Proxy instance bound to a unique loopback port.

* **Microsoft Entra ID integration**
  Centralized identity, MFA enforcement, token issuance, and claim validation.

* **Strict redirect and cookie controls**
  Ensures secure handling of user sessions and identity metadata.

* **Identity header injection**
  Provides downstream services with validated user details.

---

## 🔄 Authentication Flow

### ASCII Diagram

```
User Browser → Nginx → oauth2-proxy → Microsoft Entra ID
                    ↘ authenticated ↙
                          Backend
```

### Step-by-Step Table

| Step | Component           | Description                                             |
| ---- | ------------------- | ------------------------------------------------------- |
| 1    | User Browser        | Requests `https://code.refol.us`                        |
| 2    | Nginx               | Calls `auth_request /oauth2/auth`                       |
| 3    | OAuth2 Proxy        | Validates session; redirects to Entra ID if none exists |
| 4    | Microsoft Entra ID  | Authenticates user, issues ID/Access tokens             |
| 5    | OAuth2 Proxy        | Validates tokens, sets identity headers                 |
| 6    | Nginx               | Forwards authenticated request to backend               |
| 7    | Backend Application | Processes request with verified identity                |

---

## 🧾 Identity Headers and Mapping

| Header                              | Meaning / Use Case                | Controlled By                      |
| ----------------------------------- | --------------------------------- | ---------------------------------- |
| `X-Auth-Request-User`               | User’s UPN/username               | `set_xauthrequest = true`          |
| `X-Auth-Request-Email`              | Full user email                   | `set_xauthrequest = true`          |
| `X-Auth-Request-Access-Token`       | Raw access token                  | `pass_access_token = true`         |
| `Authorization: Bearer <token>`     | Standard OAuth2 bearer header     | `pass_authorization_header = true` |
| `X-Auth-Request-Preferred-Username` | Preferred username claim          | `set_xauthrequest = true`          |
| `X-Auth-Request-Groups`             | AD group memberships (if exposed) | `set_xauthrequest = true`          |

---

## ✅ Summary

* **Authentication** comes from Microsoft Entra ID.
* **OAuth2 Proxy** validates tokens and injects identity headers.
* **Nginx** enforces authentication with `auth_request`.
* **Backend services** receive identity data without implementing OAuth2.
* **Per-domain isolation** ensures predictable, maintainable automation.
* **Security and observability** are built-in via strict cookie and logging controls.
