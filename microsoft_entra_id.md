# 🔐 Microsoft Entra ID

**Microsoft Entra ID** (formerly Azure Active Directory) is the cloud‑based identity and access management platform used in the homelab to provide **centralized authentication**, **OAuth2 identity services**, and **secure application access**.  
In this environment, Entra ID acts as the **primary OAuth2 provider** for internal applications protected behind the reverse proxy, enabling modern authentication flows without maintaining local identity infrastructure.

Entra ID integrates seamlessly with the homelab’s automation stack, allowing service principals, OAuth2 clients, and application registrations to be provisioned programmatically using Ansible.

---

## 📘 Related Pages

### ✅ [[Entra ID OAuth2 Provisioning Ansible Role]]
Automates the creation and configuration of OAuth2 applications, redirect URIs, secrets, and permissions in Entra ID using Ansible.

---

### ✅ [[Create a Service Principal in Microsoft Entra ID]]
Step‑by‑step instructions for creating a service principal, assigning roles, and preparing credentials for use with automation tools and OAuth2‑protected services.

---

### ✅ [[Reverse Proxy Frontend Server Configuration (with_OAuth2_Support)]]
Configuration guide for the homelab’s Nginx frontend server — managing TLS, backend routing, and Microsoft Entra ID OAuth2 authentication for protected sites.

---

## 🧩 How Entra ID Fits Into the Homelab

- Acts as the **central identity provider** for OAuth2 Proxy  
- Provides **secure login** for internal web applications  
- Supports **MFA**, conditional access, and modern identity governance  
- Integrates with **Ansible automation** for repeatable provisioning  
- Eliminates the need for maintaining local OAuth servers  

---

## ✅ Summary

This page serves as the central hub for all Microsoft Entra ID–related documentation in the homelab. Use the links above to explore automation workflows, service principal creation, and OAuth2 provisioning patterns.

