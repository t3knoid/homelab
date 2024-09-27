# Join an Ubuntu 24.04 VM to Active Directory Domain

## Systems Requirement

Windows DNS Server must be installed in the Windows Domain controller.

Configure Pi-Hole  DNS Setting Conditional Forwarding to point to the AD host (e.g. 192.168.2.251).

## Install Required Packages

```bash
sudo apt update
sudo apt -y install realmd sssd sssd-tools libnss-sss libpam-sss adcli samba-common-bin oddjob oddjob-mkhomedir packagekit
```

## Verify the Domain is Discoverable via DNS

```bash
sudo realm -v discover refol.us
 * Resolving: _ldap._tcp.refol.us
 * Performing LDAP DSE lookup on: 192.168.2.252
 ! Can't contact LDAP server
 * Performing LDAP DSE lookup on: 192.168.2.251
 * Successfully discovered: refol.us
refol.us
  type: kerberos
  realm-name: REFOL.US
  domain-name: refol.us
  configured: no
  server-software: active-directory
  client-software: sssd
  required-package: sssd-tools
  required-package: sssd
  required-package: libnss-sss
  required-package: libpam-sss
  required-package: adcli
  required-package: samba-common-bin
```

## Point DNS Setting to Active Directory Server

Edit /etc/netplan/50-cloud-init.yaml and set the DNS server to the active directory server.

The following points the nameserver to 192.168.2.251.

```bash
network:
    ethernets:
        enp6s18:
          addresses:
            - 192.168.2.101/24
          nameservers:
            addresses:
            - 192.168.2.251
            - 192.168.2.252
            search:
            - refol.us
          routes:
            - to: default
              via: 192.168.2.1
    version: 2
```

Apply change.

```bash
sudo netplan apply
```

## Verify DNS Server

```bash
resolvectl status
```

## Discover Active Directory Domain

```bash
frank@ubuntu:~$ sudo realm discover refol.us
refol.us
  type: kerberos
  realm-name: REFOL.US
  domain-name: refol.us
  configured: no
  server-software: active-directory
  client-software: sssd
  required-package: sssd-tools
  required-package: sssd
  required-package: libnss-sss
  required-package: libpam-sss
  required-package: adcli
  required-package: samba-common-bin
```
## Join Machine to Domain

Run the following command to join the machine to the domain.

```bash
sudo realm join -v refol.us

 * Resolving: _ldap._tcp.refol.us
 * Performing LDAP DSE lookup on: 192.168.2.251
 * Successfully discovered: refol.us
Password for Administrator:
 * Unconditionally checking packages
 * Resolving required packages
 * LANG=C /usr/sbin/adcli join --verbose --domain refol.us --domain-realm REFOL.US --domain-controller 192.168.2.251 --login-type user --login-user Administrator --stdin-password
 * Using domain name: refol.us
 * Calculated computer account name from fqdn: ANSIBLE-0
 * Using domain realm: refol.us
 * Sending NetLogon ping to domain controller: 192.168.2.251
 * Received NetLogon info from: ad0.refol.us
 * Wrote out krb5.conf snippet to /var/cache/realmd/adcli-krb5-yY9G0T/krb5.d/adcli-krb5-conf-1S8afK
 * Authenticated as user: Administrator@REFOL.US
 * Using GSS-SPNEGO for SASL bind
 * Looked up short domain name: REFOL
 * Looked up domain SID: S-1-5-21-1130932204-1436355067-3084612927
 * Received NetLogon info from: ad0.refol.us
 * Using fully qualified name: ansible-0
 * Using domain name: refol.us
 * Using computer account name: ANSIBLE-0
 * Using domain realm: refol.us
 * Calculated computer account name from fqdn: ANSIBLE-0
 * Generated 120 character computer password
 * Using keytab: FILE:/etc/krb5.keytab
 * Found computer account for ANSIBLE-0$ at: CN=ANSIBLE-0,CN=Computers,DC=refol,DC=us
 * Trying to set computer password with Kerberos
 * Set computer password
 * Retrieved kvno '3' for computer account in directory: CN=ANSIBLE-0,CN=Computers,DC=refol,DC=us
 * Checking RestrictedKrbHost/ANSIBLE-0
 *    Added RestrictedKrbHost/ANSIBLE-0
 * Checking host/ANSIBLE-0
 *    Added host/ANSIBLE-0
 * Discovered which keytab salt to use
 * Added the entries to the keytab: ANSIBLE-0$@REFOL.US: FILE:/etc/krb5.keytab
 * Added the entries to the keytab: host/ANSIBLE-0@REFOL.US: FILE:/etc/krb5.keytab
 * Added the entries to the keytab: RestrictedKrbHost/ANSIBLE-0@REFOL.US: FILE:/etc/krb5.keytab
 * /usr/sbin/update-rc.d sssd enable
 * /usr/sbin/service sssd restart
 * Successfully enrolled machine in realm
```

Enter the domain administrator's password when prompted.

## View the Current Realmd Details

To view our current realmd details, we run the realm list command. The output should be similar to that of realm discover.

```bash
sudo realm list
```

## sssd.conf File and Home Directory

By default, the realm command has already configured this file. It added the pam and nss modules and started the necessary services.

```bash
frank@ansible-0:~$ sudo cat /etc/sssd/sssd.conf
```

```ini
[sssd]
domains = refol.us
config_file_version = 2
services = nss, pam

[domain/refol.us]
default_shell = /bin/bash
krb5_store_password_if_offline = True
cache_credentials = True
krb5_realm = REFOL.US
realmd_tags = manages-system joined-with-adcli
id_provider = ad
fallback_homedir = /home/%u@%d
ad_domain = refol.us
use_fully_qualified_names = True
ldap_id_mapping = True
access_provider = ad
```

Note:
Something very important to remember is that this file must have permissions 0600 and ownership root:root, or else SSSD won’t start!

From the configurations file, we can observe a few things:

The cache_credentials setting is set to True. Thus, a user can still log in even if the Active Directory is unavailable.
The fallback_homedir is /home/%u@%d. For example, a user will have a home directory of /home/user@domain.

The use_fully_qualified_names is set to True. As a result, users must log in using the format user@domain.

The realm command doesn’t set up pam_mkhomedir. Let’s configure it:

```bash
sudo pam-auth-update --enable mkhomedir
```

## Verify Connected to Domain Controller

```bash
frank@ansible-0:~$ sudo realm -v discover refol.us
 * Resolving: _ldap._tcp.refol.us
 * Resolving: refol.us
 * Performing LDAP DSE lookup on: 192.168.2.251
 * Successfully discovered: refol.us
refol.us
  type: kerberos
  realm-name: REFOL.US
  domain-name: refol.us
  configured: kerberos-member
  server-software: active-directory
  client-software: sssd
  required-package: sssd-tools
  required-package: sssd
  required-package: libnss-sss
  required-package: libpam-sss
  required-package: adcli
  required-package: samba-common-bin
  login-formats: %U@refol.us
  login-policy: allow-realm-logins
  ```

## Verify Domain Group and User Access

```bash
frank@ansible-0:~$ sudo getent passwd frank@refol.us
frank@refol.us:*:873401104:873400513:Frank Refol:/home/frank@refol.us:/bin/bash
```

```bash
sudo id frank@refol.us
uid=873401104(frank@refol.us) gid=873400513(domain users@refol.us) groups=873400513(domain users@refol.us),873400512(domain admins@refol.us),873400572(denied rodc password replication group@refol.us)
```

## SSSD Log

```bash
sudo tail -f /var/log/sssd/sssd_refol.us.log
```

## Add User to Sudoers Group

```bash
sudo usermod -a -G sudo frank@refol.us
```

## References

- https://www.server-world.info/en/note?os=Ubuntu_24.04&p=realmd
- https://ubuntu.com/server/docs/how-to-set-up-sssd-with-active-directory