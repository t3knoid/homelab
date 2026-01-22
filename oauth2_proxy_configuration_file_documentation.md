---
title: "OAuth2 Proxy Configuration File Documentation"
---

# OAuth2 Proxy Configuration File Documentation

The following sections describe the common configuration properties used in an **OAuth2 Proxy** `.cfg` file and explain how each setting affects authentication behavior, security, and integration with upstream services.

---

## 🖥️ Server Settings

* **`http_address = "127.0.0.1:4181"`**
  The address and port where OAuth2 Proxy listens for internal authentication requests.

  * `127.0.0.1` restricts access to the local machine only.
  * `4181` is the unique port assigned to this proxy instance.

---

## 🔑 Identity Provider Settings

* **`provider = "azure"`**
  Selects Microsoft Entra ID (Azure AD) as the OpenID Connect (OIDC) provider.

* **`client_id = "YOUR_AZURE_APP_CLIENT_ID"`**
  The application’s Client ID registered in Azure AD.

* **`client_secret = "YOUR_AZURE_APP_CLIENT_SECRET"`**
  The application’s secret, used by OAuth2 Proxy to authenticate with Microsoft Entra ID.

* **`oidc_issuer_url = "https://login.microsoftonline.com/YOUR_TENANT_ID/v2.0"`**
  The OIDC issuer URL for your Azure AD tenant. OAuth2 Proxy uses it to validate tokens.

---

## 🔄 Redirect Settings

* **`redirect_url = "https://wiki.refol.us/oauth2/callback"`**
  The callback endpoint where users are returned after successful login.

  * Must exactly match the redirect URI registered in Azure AD.
  * Typically `/oauth2/callback` on the protected domain.

---

## 🍪 Cookie Settings

* **`cookie_secret = "SHARED_RANDOM_32_BYTE_STRING_BASE64"`**
  A base64-encoded random 32-byte value used for encrypting and signing session cookies. 

  * Shared across instances if load balanced.
  * Generate with: `python -c 'import os,base64; print(base64.urlsafe_b64encode(os.urandom(32)).decode())'`.

* **`cookie_secure = false`**
  Enables the Secure flag on cookies.

  * `false`: cookies can be transmitted over HTTP (local testing).
  * `true`: **required in production**—HTTPS only.

* **`cookie_http_only = true`**
  Marks cookies as HTTP-only, preventing JavaScript access.

  * Helps mitigate XSS attacks.

---

## 🗄️ Session Storage Settings

OAuth2 Proxy supports two mechanisms for persisting session data: encrypted browser cookies or a centralized Redis backend.  
Using Redis is recommended for high‑availability deployments, multi‑instance scaling, or when you want to minimize cookie size.

### Session data storage backend  

* **`session_store_type = "redis"`**
  Selects Redis as the session storage backend instead of client‑side cookies.  

### Redis connection URL  

* **`redis_connection_url = "REDIS_SERVER_URL"`**
  Defines the Redis server used for session storage.

This value is templated from the `oauth2_proxy_setup_redis_connection` variable, ensuring consistent configuration across all OAuth2 Proxy instances.

---

## 🔐 Access Control

* **`email_domains = ["*"]`**
  Defines allowed email domains.

  * `["*"]` permits all domains.
  * Restrict to organizational domains, e.g. `["refol.us"]`, to enhance security.

---

## 🏷️ Header & Token Behavior

* **`set_xauthrequest = true`**
  Enables forwarding of headers used by Nginx for auth checks
  (`X-Auth-Request-User`, `X-Auth-Request-Email`, etc.).

* **`pass_access_token = true`**
  Passes the OAuth2 access token to the upstream via `X-Auth-Request-Access-Token`.

* **`pass_authorization_header = true`**
  Forwards the standard `Authorization: Bearer <token>` header.

  * Enable only if the backend expects bearer tokens.

---

## 🧭 Best Practices for OAuth2 Proxy Configuration

### 🔐 Security

* **Set `cookie_secure = true` in production**
  Prevents cookies from being sent over insecure channels.

* **Rotate `cookie_secret` regularly**
  Use strong randomness and store securely.

* **Restrict `email_domains`**
  Avoid using `["*"]` unless absolutely necessary.

* **Limit token forwarding**
  Only enable token headers if the application explicitly requires them.

---

### ⚙️ Maintainability

* **Use dictionary-based port mapping**
  Keeps ports organized and prevents collisions.

* **Follow consistent service naming**
  Standardize as `oauth2-proxy_{{ server_name }}.service`.

* **Use templated configs**
  Generate `.cfg` files via Ansible to ensure idempotency and consistency.

---

### 🛠️ Operational Practices

* **Monitor logs**
  Watch for authentication failures or misconfigurations.

* **Enable local health checks**
  Helps detect failed OAuth2 Proxy instances quickly.

* **Rotate Azure secrets**
  Refresh `client_secret` before expiration.

---

### 🚀 Deployment Tips

* **Use Unix sockets (optional)**
  Instead of ports: `/run/oauth2-proxy/{{ server_name }}.sock`.

* **Automate cleanup**
  Remove unused configs/services when `use_oauth2` is false.

* **Validate redirect URIs**
  Any mismatch with Azure AD will immediately break login flows.