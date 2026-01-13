---
title: "Microsoft Entra ID"
---

# 🔐 Microsoft Entra ID

Microsoft Entra ID (formerly Azure Active Directory) is the cloud‑based identity and access management platform used in the homelab to provide centralized authentication, OAuth2 identity services, and secure application access.  
In this environment, Entra ID acts as the primary OAuth2 provider for internal applications protected behind the reverse proxy, enabling modern authentication flows without maintaining local identity infrastructure.

Entra ID integrates seamlessly with the homelab’s automation stack, allowing service principals, OAuth2 clients, and application registrations to be provisioned programmatically using Ansible.

---

## 🧩 How Entra ID Fits Into the Homelab
- Acts as the central identity provider for OAuth2 Proxy  
- Provides secure login for internal web applications  
- Supports MFA, conditional access, and modern identity governance  
- Integrates with Ansible automation for repeatable provisioning  
- Eliminates the need for maintaining local OAuth servers

---

## 🧱 Core Concepts

### 🧩 Service Principal

**Think of a Service Principal as the cloud‑native equivalent of a service account — but designed specifically for applications rather than users.**  Where a service account is a user identity with a password, a Service Principal is an application identity that authenticates using client credentials (secret or certificate) and receives RBAC‑scoped access to Azure resources.  It’s the secure, modern way for automation tools in the homelab to interact with Entra ID.

#### Why It Matters Here
- Enables non‑interactive authentication for automation (Ansible, CI/CD, scripts)  
- Provides isolated, least‑privilege access to Azure resources  
- Supports certificate‑based authentication for improved security  
- Avoids using user accounts for automation workflows  

---

### 🔐 RBAC (Role‑Based Access Control)

RBAC is an access‑control model where permissions are assigned to **roles**, and identities gain permissions only by being assigned those roles.  
It simplifies authorization by managing access at the role level instead of the individual level.

#### Homelab Usage

- Assign minimal roles to Service Principals (e.g., Reader, Contributor)  
- Keep automation scoped to only the resources it needs  
- Avoid tenant‑wide permissions unless absolutely required  

---

### 🔑 Credential Types

#### Client Secret

- Simple to generate  
- Easy to automate  
- Must be rotated regularly  
- Stored securely in Ansible Vault or your secret‑management workflow

#### Certificate Authentication

- Stronger security posture  
- Longer‑lived and harder to exfiltrate  
- Ideal for long‑running automation or CI/CD pipelines

#### OAuth2 Client Credentials Flow

Used by:

- OAuth2 Proxy  
- Internal apps behind the reverse proxy  
- Ansible provisioning role  
- Any automation that needs tokens from Entra ID

---

## Diagram: App Registration → Service Principal → RBAC

THe following illustrates the relationship between the afformentioned core concepts of Microsoft Entra ID.

{% raw %}
```
                ┌──────────────────────────┐
                │   Application Object     │
                │  (App Registration)      │
                │                          │
                │  • Global definition     │
                │  • Client ID             │
                │  • Redirect URIs         │
                │  • API permissions       │
                └─────────────┬────────────┘
                              │
                              ▼
                ┌───────────────────────────┐
                │     Service Principal     │
                │   (Enterprise App)        │
                │                           │
                │  • Instance of the app    │
                │  • Auth via secret/cert   │
                │  • Identity for automation│
                └─────────────┬─────────────┘
                              │
                              ▼
                ┌───────────────────────────┐
                │           RBAC            │
                │  Role Assignments         │
                │                           │
                │  • Reader / Contributor   │
                │  • Least‑privilege access │
                │  • Scoped to resources    │
                └───────────────────────────┘
```
{% endraw %}

# 📘 Related Pages

- **[Entra ID OAuth2 Provisioning Ansible Role](entra_id_oauth2_provisioning_ansible_role.md)** — Automates the creation and configuration of OAuth2 applications, redirect URIs, secrets, and permissions in Entra ID using Ansible.
- **[Service Principal](service_principal.md)** — Step‑by‑step instructions for creating a service principal, assigning roles, and preparing credentials for automation tools and OAuth2‑protected services.
- **[Application Registration](application_registration.md)** - Step-by-step instructions on configuring an Application Registration.
- **[OAuth2 Proxy Integration with Entra ID](oauth2_proxy_integration_with_entra_id.md)** — Configuration guide for the homelab’s Nginx frontend server, managing TLS, backend routing, and Entra ID OAuth2 authentication for protected sites.
- **[Contributor Guide Adding Entra ID OAuth2 Support for a Web Service](contributor_guide_adding_entra_id_oauth2_support_for_a_web_service.md)** - Provides a step-by-step instructions on configuring a web service to use Entra ID as an Oauth2 identity provider using Ansible.

---

# ✅ Summary
This page serves as the central hub for all Microsoft Entra ID–related documentation in the homelab.

Use the links above to explore automation workflows, service principal creation, and OAuth2 provisioning patterns.