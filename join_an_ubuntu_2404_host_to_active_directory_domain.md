# 🔗 Joining an Ubuntu 24.04 Host to Active Directory

This guide details the process of joining an **Ubuntu 24.04** host to the **refol.us Active Directory domain**.  
It assumes an Active Directory Domain Controller is available at **192.168.2.251**.  
> 💡 Note: In production, this process can be automated using **Ansible** during host provisioning.

---

## 1️⃣ System Requirements

- **Windows DNS Server** must be installed and running on the Domain Controller.  
- **Pi‑hole DNS** should be configured with **Conditional Forwarding** to point to the AD host, ensuring proper resolution of domain records.

---

## 2️⃣ Install Required Packages

Update the system and install the necessary packages for realm discovery, SSSD integration, and AD joining:

```bash
sudo apt update
sudo apt -y install realmd sssd sssd-tools libnss-sss libpam-sss adcli samba-common-bin oddjob oddjob-mkhomedir packagekit
```

---

## 3️⃣ Configure DNS to Point to Active Directory

Edit the Netplan configuration (`/etc/netplan/50-cloud-init.yaml`) to use the AD DNS server:

```yaml
network:
    ethernets:
        enp6s18:
          addresses:
            - 192.168.2.101/24
          nameservers:
            addresses:
            - 192.168.2.253
            - 192.168.2.251
            search:
            - refol.us
          routes:
            - to: default
              via: 192.168.2.1
    version: 2
```

Apply the changes:

```bash
sudo netplan apply
```

---

## 4️⃣ Discover the Active Directory Domain

Use `realm discover` to confirm the AD domain is visible:

```bash
sudo realm discover refol.us
```

Expected output (note `configured: no` before joining):

```
refol.us
  type: kerberos
  realm-name: REFOL.US
  domain-name: refol.us
  configured: no
  server-software: active-directory
  client-software: sssd
```

---

## 5️⃣ Join the Machine to the Domain

Run the join command:

```bash
sudo realm join -v refol.us
```

You will be prompted for the **Administrator password**.  
Successful output confirms enrollment and creation of the computer account in AD.

---

## 6️⃣ Verify Domain Membership

Check the realm configuration:

```bash
sudo realm list
```

Expected output:

```
refol.us
  type: kerberos
  realm-name: REFOL.US
  domain-name: refol.us
  configured: kerberos-member
  server-software: active-directory
  client-software: sssd
  login-formats: %U@refol.us
  login-policy: allow-realm-logins
```

---

## 7️⃣ Configure `sssd.conf` and Home Directory

By default, `realm join` configures `/etc/sssd/sssd.conf`.  
To simplify logins and home directory paths:

```ini
[domain/refol.us]
use_fully_qualified_names = False
fallback_homedir = /home/%u
```

Restart SSSD:

```bash
sudo service sssd restart
```

> ⚠️ **Important:** Ensure `sssd.conf` has permissions `0600` and ownership `root:root`. Otherwise, SSSD will fail to start.

---

## 8️⃣ Enable Automatic Home Directory Creation

Configure PAM to create home directories on first login:

```bash
sudo pam-auth-update --enable mkhomedir
```

---

## 9️⃣ Verify Domain User and Group Access

Check user resolution:

```bash
sudo getent passwd frank@refol.us
```

Check group memberships:

```bash
sudo id frank@refol.us
```

> 🔒 Note: The **“Denied RODC Password Replication”** group prevents caching of privileged account credentials on Read‑Only Domain Controllers, enhancing security.

---

## 🔟 Monitor SSSD Logs

For troubleshooting authentication issues:

```bash
sudo tail -f /var/log/sssd/sssd_refol.us.log
```

---

## 1️⃣1️⃣ Grant Sudo Access to Domain Users

Add a domain user to the sudo group:

```bash
sudo usermod -a -G sudo frank@refol.us
```

---

## 📚 References

- [Server‑World: Ubuntu 24.04 + Active Directory Integration](https://www.server-world.info/en/note?os=Ubuntu_24.04&p=realmd)  
- [Ubuntu Docs: SSSD with Active Directory](https://ubuntu.com/server/docs/how-to-set-up-sssd-with-active-directory)  

