---
title: "LDAP"
---

# 🔐 LDAP

**Lightweight Directory Access Protocol (LDAP)** is a standard protocol used to authenticate and query directory services such as **Active Directory (AD)**. In this environment, LDAP provides centralized authentication for applications that support directory integration, ensuring consistent identity management across systems.

---

## 👤 LDAP Service Account

Applications bind to the domain controller using a dedicated service account. This account should follow **least‑privilege principles** and be restricted to read‑only access.

- **Username:** `ldap_bind_user`  
- **Distinguished Name (DN):**  
  ```
  CN=LDAP Bind User,OU=Service Accounts,DC=refol,DC=us
  ```

> ⚠️ Avoid using privileged accounts for LDAP binds. Rotate credentials regularly and monitor usage.

---

## 🧪 Testing LDAP Connectivity with Python

You can validate LDAP connectivity using the **python‑ldap** library.

### 1. Install prerequisites
{% raw %}
```shell
sudo apt-get install build-essential python3-dev \
    libldap2-dev libsasl2-dev slapd ldap-utils tox \
    lcov valgrind
python -m pip install python-ldap
```
{% endraw %}

### 2. Example test script
{% raw %}
```python
import ldap
import logging

logging.basicConfig(level=logging.DEBUG)

ldap_server = "ldap://192.168.2.251"
bind_dn = "CN=LDAP Bind User,OU=Service Accounts,DC=refol,DC=us"
password = "mysecurepassword"
search_base = "CN=Users,DC=refol,DC=us"
search_filter = "(sAMAccountName=frank)"  # Replace with your search filter

try:
    ldap_connection = ldap.initialize(ldap_server)
    ldap_connection.set_option(ldap.OPT_REFERRALS, 0)  # Important for AD
    ldap_connection.simple_bind_s(bind_dn, password)
    print("LDAP bind successful")

    result = ldap_connection.search_s(search_base, ldap.SCOPE_SUBTREE, search_filter)
    print("LDAP search result:", result)

except ldap.INVALID_CREDENTIALS:
    print("Invalid credentials")
except ldap.LDAPError as e:
    print("LDAP error:", e)
finally:
    ldap_connection.unbind_s()
```
{% endraw %}

---

## 📑 Best Practices

- **Use secure transport:** Prefer LDAPS (TCP 636) or StartTLS on LDAP (TCP 389).  
- **Limit search scope:** Restrict search bases to relevant OUs.  
- **Referral handling:** Disable referrals (`ldap.OPT_REFERRALS = 0`) unless multi‑domain queries are required.  
- **Service account hygiene:** Rotate passwords, enforce read‑only permissions, and audit usage.  

---

## 📊 Common LDAP Filters Quick Reference

| Purpose                  | Attribute             | Example Filter                          |
|---------------------------|-----------------------|-----------------------------------------|
| By username (SAM)         | `sAMAccountName`      | `(sAMAccountName=frank)`                |
| By UPN (email‑style logon)| `userPrincipalName`   | `(userPrincipalName=frank@refol.us)`    |
| By email address          | `mail`                | `(mail=frank@refol.us)`                 |
| By common/display name    | `cn`                  | `(cn=Frank Smith)`                      |
| By group membership       | `memberOf`            | `(memberOf=CN=Admins,OU=Groups,DC=refol,DC=us)` |
| By enabled accounts only  | `userAccountControl`  | `(!(userAccountControl:1.2.840.113556.1.4.803:=2))` |
| By disabled accounts      | `userAccountControl`  | `(userAccountControl:1.2.840.113556.1.4.803:=2)` |

---

## 🔗 LDAP Attribute Mapping

When integrating LDAP with applications (e.g., Semaphore, Jenkins, GitLab), attributes must be mapped correctly to application fields. Below is a common mapping reference:

| Application Field | AD Attribute        | Notes                                                                 |
|-------------------|---------------------|----------------------------------------------------------------------|
| **uid**           | `sAMAccountName`    | The Windows logon name (e.g., `frank`). Often used as the username.  |
| **mail**          | `userPrincipalName` | Preferred for unique identification; can also use `mail` attribute.  |
| **cn**            | `cn`                | Common name (display name).                                          |
| **dn**            | Distinguished Name  | Full LDAP path to the user object.                                   |
| **groups**        | `memberOf`          | Lists group memberships; useful for role‑based access control.       |
| **givenName**     | `givenName`         | User’s first name.                                                   |
| **sn**            | `sn`                | User’s surname (last name).                                          |

> 💡 Many applications allow custom mapping. Always verify which attributes are required and adjust filters accordingly.

---

## 🛠 Troubleshooting Checklist

- **Connectivity:** Verify ports (389/636) and DNS resolution.  
- **Bind failures:** Check credentials, DN formatting, and account status.  
- **Search issues:** Validate search base and filter syntax.  
- **TLS problems:** Ensure certificates are trusted and CN/SAN matches the domain controller hostname.  

---

## 📚 References

- [Microsoft LDAP Overview (Windows Server 2008 R2)](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2008-R2-and-2008/cc816778(v=ws.10)?redirectedfrom=MSDN)  
- [Install Windows Features with PowerShell](https://learn.microsoft.com/en-us/powershell/module/servermanager/install-windowsfeature?view=windowsserver2022-ps)  
- [Active Directory LDAP Integration](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2008-R2-and-2008/cc816774(v=ws.10)?redirectedfrom=MSDN)  

