---
title: "Service Principal"
---

# 🧩 Service Principal  

A **Service Principal** is the *application identity* that Microsoft Entra ID creates from an Application Registration. It represents the actual, usable identity that applications, scripts, and automation tools authenticate as when interacting with Azure or requesting OAuth2 tokens.

Where the **Application Registration** defines the **blueprint** of an app, the **Service Principal** is the **instance** of that app within your tenant. It holds the permissions, RBAC role assignments, and credential usage that determine what the application can do.

This page explains **what a Service Principal is** and **how to configure one** for use in the homelab.

---

## 🎯 Purpose in the homelab  

Service Principals are used to:

- **Provide non‑interactive authentication** for automation (Ansible, CI/CD, scripts)  
- **Authenticate internal services** that need OAuth2 tokens  
- **Receive RBAC roles** for scoped access to Azure resources  
- **Avoid using user accounts** for automation  
- Support both **client secrets** and **certificate‑based** authentication  

In short:  

- **Application Registration = identity definition**  
- **Service Principal = identity instance used by automation**

---

# 🛠️ How to create and configure a Service Principal  

A Service Principal is created automatically when you register an application, but you still need to **generate credentials** and **assign permissions** so automation can use it.

The homelab uses the following pattern.

---

## 1️⃣ Create an application registration  

A Service Principal cannot exist without an Application Registration.

1. **Go to:**  
   **Azure Portal → Microsoft Entra ID → App registrations → New registration**
2. **Name:**  
   Use a clear, homelab‑consistent pattern (for example: `homelab-oauth2-proxy`, `ansible-automation`, `grafana-internal`).
3. **Supported account types:**  
   - **Single tenant** (recommended for the homelab).
4. **Redirect URI (optional):**  
   - Required for OAuth2 Proxy and web apps (for example `https://<your-domain>/oauth2/callback`).  
   - Not required for pure automation (client‑credentials only).

Click **Register**.

This creates:

- The **Application Registration**  
- The associated **Service Principal** in your tenant

---

## 2️⃣ Create a client secret (or certificate)  

The Service Principal needs credentials to authenticate.

1. Open the **Application Registration** you just created.  
2. Go to **Certificates & secrets → Client secrets → New client secret**.  
3. Add a description (for example: `ansible-automation`, `oauth2-proxy`).  
4. Choose an appropriate **expiry** (based on your rotation policy).  
5. Click **Add**, then **copy the Value immediately**.

Store the **client secret value** securely (for example in **Ansible Vault** or your secrets workflow).  
You will not be able to view this value again later.

> If using certificates instead of secrets, upload the public certificate here and configure your automation to use the matching private key.

---

## 3️⃣ Get tenant and subscription information  

You’ll need these values for automation tools.

1. **Tenant ID**  
   - Go to **Microsoft Entra ID → Overview**.  
   - Copy the **Tenant ID**.

2. **Subscription ID** (required if RBAC access to Azure resources is needed)  
   - Go to **Subscriptions → Your subscription**.  
   - Copy the **Subscription ID**.

---

## 4️⃣ Locate the service principal  

To view or reference the identity itself:

1. Go to **Microsoft Entra ID → Enterprise applications → All applications**.  
2. Search for the same **name** as your Application Registration.  
3. Open it — this object is the **Service Principal**.

This is the identity that:

- Shows up in RBAC assignments  
- Appears in **Sign‑ins**  
- Represents the application when it authenticates

---

## 5️⃣ Assign RBAC roles (if the service needs Azure access)  

If the Service Principal needs to access Azure resources (for example, for Ansible automation):

1. Go to the **scope** where permissions are required:  
   - Subscription  
   - Resource group  
   - Specific resource
2. Open **Access control (IAM)**.  
3. Click **Add → Add role assignment**.  
4. Select the appropriate **role** (for example: `Reader`, `Contributor`, `Storage Blob Data Contributor`).  
5. In **Members**, choose **User, group, or service principal**.  
6. Search for and select the **Service Principal** (it appears under Enterprise applications).  
7. Confirm and save the assignment.

Roles are always assigned to the **Service Principal**, not the Application Registration.

Use **least‑privilege** wherever possible.

---

## 6️⃣ Collect the values used by automation  

Most automation workflows in the homelab require the following four values:

- **Client ID** — from the Application Registration’s **Overview**  
- **Client Secret** — created in **Certificates & secrets**  
- **Tenant ID** — from **Microsoft Entra ID → Overview**  
- **Subscription ID** — from **Subscriptions → Overview** (if Azure RBAC is used)

These values allow the Service Principal to authenticate via the **OAuth2 client‑credentials flow** and obtain access tokens.

Store all of them securely.

---

# 🔐 Credentials and token usage  

Service Principals authenticate using:

- **Client ID + client secret**, or  
- **Client ID + certificate**

They then request tokens from Microsoft Entra ID (token endpoint) using the **client‑credentials** flow and use those tokens to:

- Call Azure APIs  
- Integrate with reverse‑proxy/OAuth2 workflows  
- Perform automated tasks via Ansible or CI/CD

---

# 🔗 Related pages  

- **[Application Registration](application_registration.md)** — Defines the blueprint that Service Principals are created from  
- **[Entra ID OAuth2 Provisioning Ansible Role](entra_id_oauth2_provisioning_ansible_role.md)** — Automates creation of apps, secrets, and Service Principals  
- **[Reverse Proxy Frontend Server Configuration](reverse_proxy_frontend_server_configuration.md)** — How OAuth2 Proxy integrates with Nginx and Entra ID  

