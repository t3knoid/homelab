---
title: "Create a Service Principal in Microsoft Entra ID"
---

# Create a Service Principal in Microsoft Entra ID


## 📘 Step‑by‑Step in the Entra ID UI

### 1. Register a New Application
1. Sign in to [Azure Portal](https://portal.azure.com).  
2. Navigate to **Microsoft Entra ID** → **App registrations**.  
3. Click **+ New registration**.  
4. Fill in:
   - **Name** → Friendly name (e.g., `ansible`).  
   - **Supported account types** → Usually “Accounts in this organizational directory only.”  
   - **Redirect URI** → Optional unless you plan to use OAuth flows.  
5. Click **Register**.  
👉 This creates the **Application (client) ID** and the associated **service principal** in your tenant.

---

### 2. Create a Client Secret
1. In your new app registration, go to **Certificates & secrets**.  
2. Under **Client secrets**, click **+ New client secret**.  
3. Add a description and choose an expiration period.  
4. Click **Add**.  
5. Copy the **Value** immediately — this is your **Client Secret**.  
   ⚠️ Important: You won’t be able to see it again later.

---

### 3. Get Tenant ID
- In **Microsoft Entra ID** → **Overview**, copy the **Tenant ID** (Directory ID).  

---

### 4. Assign RBAC Permissions
1. Go to **Subscriptions** in the portal.  
2. Select your subscription.  
3. Click **Access control (IAM)** → **+ Add role assignment**.  
4. In the wizard:
   - **Role** → Pick Contributor (or whatever role you want, e.g. Privileged administrator roles > Contributor).  
   - **Assign access to** → Change this from *User, group, or service principal* to specifically include **service principal**.  
   - **Members** → Click **+ Select members**.  
5. In the search box, type the **name of your app registration** (the friendly name you gave it when you registered).  
   - It will appear under **Enterprise applications**.  
   - Select it, then click **Review + assign**.

---

### 5. Collect the Four Values
You now have:
- **Client ID** → Application (client) ID from the app registration.  
- **Client Secret** → Value from Certificates & secrets.  
- **Tenant ID** → Directory ID from Entra ID overview.  
- **Subscription ID** → From Subscriptions overview.  

These four values are what Ansible uses to authenticate and obtain tokens.

---

## ✅ Summary
- In the Entra ID UI, you **register an app** → this creates the service principal.  
- You then **create a client secret** and **assign RBAC permissions**.  
- Collect **Client ID, Client Secret, Tenant ID, Subscription ID**.  
- Store them securely (e.g., Ansible Vault) and use them in your automation.




