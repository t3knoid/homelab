# Join Proxmox host to active directory

The following process joins a Proxmox VE server to the refol.us active directory domain. These instructions assumes an active directory server is on IP 192.168.2.251.

## Systems Requirement

The following are required.

* Windows DNS Server must be installed in the Windows Domain controller.
* Configure Pi-Hole DNS Setting Conditional Forwarding to point to the AD host.

## Install Required Packages

``` shell
sudo apt update
sudo apt -y install realmd sssd sssd-tools libnss-sss libpam-sss adcli samba-common-bin oddjob oddjob-mkhomedir packagekit
```

## Point DNS Setting to Active Directory Server

Edit /etc/resolv.conf and set the DNS server to the active directory server.

The following points the nameserver to 192.168.2.251.

``` shell
search refol.us
nameserver 192.168.2.251
nameserver 192.168.2.252
nameserver 192.168.2.253
```
## Discover Active Directory Domain

``` shell
sudo realm discover refol.us
```
<details>
<summary>Click to show output</summary>
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
</details>

Notice that the host has not been configured to the active directory domain.

``` shell
configured: no
```

## Join Machine to Domain

Run the following command to join the machine to the domain.

``` shell
sudo realm join -v refol.us
```

<details>
<summary>Click to show output</summary>
 * Resolving: _ldap._tcp.refol.us
 * Performing LDAP DSE lookup on: 192.168.2.251
 * Successfully discovered: refol.us
Password for Administrator:
 * Unconditionally checking packages
 * Resolving required packages
 * LANG=C /usr/sbin/adcli join --verbose --domain refol.us --domain-realm REFOL.US --domain-controller 192.168.2.251 --login-type user --login-user Administrator --stdin-password
 * Using domain name: refol.us
 * Calculated computer account name from fqdn: PVE-0
 * Using domain realm: refol.us
 * Sending NetLogon ping to domain controller: 192.168.2.251
 * Received NetLogon info from: ad0.refol.us
 * Wrote out krb5.conf snippet to /var/cache/realmd/adcli-krb5-Yx8iCQ/krb5.d/adcli-krb5-conf-8XKzqK
 * Authenticated as user: Administrator@REFOL.US
 * Using GSS-SPNEGO for SASL bind
 * Looked up short domain name: REFOL
 * Looked up domain SID: S-1-5-21-1130932204-1436355067-3084612927
 * Using fully qualified name: pve-0.lan
 * Using domain name: refol.us
 * Using computer account name: PVE-0
 * Using domain realm: refol.us
 * Calculated computer account name from fqdn: PVE-0
 * Generated 120 character computer password
 * Using keytab: FILE:/etc/krb5.keytab
 * A computer account for PVE-0$ does not exist
 * Found well known computer container at: CN=Computers,DC=refol,DC=us
 * Calculated computer account: CN=PVE-0,CN=Computers,DC=refol,DC=us
 * Encryption type [3] not permitted.
 * Encryption type [1] not permitted.
 * Created computer account: CN=PVE-0,CN=Computers,DC=refol,DC=us
 * Sending NetLogon ping to domain controller: 192.168.2.251
 * Received NetLogon info from: ad0.refol.us
 * Set computer password
 * Retrieved kvno '2' for computer account in directory: CN=PVE-0,CN=Computers,DC=refol,DC=us
 * Checking RestrictedKrbHost/pve-0.lan
 *    Added RestrictedKrbHost/pve-0.lan
 * Checking RestrictedKrbHost/PVE-0
 *    Added RestrictedKrbHost/PVE-0
 * Checking host/pve-0.lan
 *    Added host/pve-0.lan
 * Checking host/PVE-0
 *    Added host/PVE-0
 * Discovered which keytab salt to use
 * Added the entries to the keytab: PVE-0$@REFOL.US: FILE:/etc/krb5.keytab
 * Added the entries to the keytab: host/PVE-0@REFOL.US: FILE:/etc/krb5.keytab
 * Added the entries to the keytab: host/pve-0.lan@REFOL.US: FILE:/etc/krb5.keytab
 * Added the entries to the keytab: RestrictedKrbHost/PVE-0@REFOL.US: FILE:/etc/krb5.keytab
 * Added the entries to the keytab: RestrictedKrbHost/pve-0.lan@REFOL.US: FILE:/etc/krb5.keytab
 * /usr/sbin/update-rc.d sssd enable
 * /usr/sbin/service sssd restart
 * Successfully enrolled machine in realm
```
</details>

Enter the domain administrator's password when prompted.

## Verify Machine has been Joined to Active Directory 

Verify the machine has been joined to Active Directory using the **realmd** command.  The output should be similar to that of realm discover.

``` shell
sudo realm list
```

<details>
<summary>Click to show output</summary>
``` shell
root@pve-0:~# sudo realm discover refol.us
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
</details>

Observe that Active Directory has been configured as shown here.

``` shell
configured: kerberos-member
```

Also notice that the login-formats is set to username@domain as shown here.

``` shell
login-formats: %U@refol.us
```

This can be modified to only use the username in the next section.

## sssd.conf File and Home Directory

By default, the realm command has already configured this file. It added the pam and nss modules and started the necessary services.

``` shell
sudo vi /etc/sssd/sssd.conf
```

``` ini
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

Edit this file so that the domain name is not needed when authenticating with a domain user.

``` shell
use_fully_qualified_names = False
```

Restart the sssd service.

``` shell
sudo service sssd restart
```

> [!IMPORTANT] 
> Something very important to remember is that this file must have permissions 0600 and ownership root:root, or else SSSD won’t start!

From the configurations file, we can observe a few things:

The cache_credentials setting is set to True. Thus, a user can still log in even if the Active Directory is unavailable.
The fallback_homedir is /home/%u@%d. For example, a user will have a home directory of /home/user@domain.

The use_fully_qualified_names is set to True. As a result, users must log in using the format user@domain.

## Enable mkhomedir

The realm command doesn’t set up pam_mkhomedir. Enabling mkhomedir will ensure that domain user home directory is created. 

``` shell
sudo pam-auth-update --enable mkhomedir
```

### Verify Domain Group and User Access

``` shell
sudo getent passwd frank@refol.us
frank@refol.us:*:873401104:873400513:Frank Refol:/home/frank@refol.us:/bin/bash
```

``` shell
sudo id frank@refol.us
uid=873401104(frank@refol.us) gid=873400513(domain users@refol.us) groups=873400513(domain users@refol.us),873400512(domain admins@refol.us),873400572(denied rodc password replication group@refol.us)
```

## SSSD Log

Monitor the SSSD log in the event of an authentication issue. 

``` shell
sudo tail -f /var/log/sssd/sssd_refol.us.log
```

## Add User to Sudoers Group

``` shell
sudo usermod -a -G sudo frank@refol.us
```

## References

- https://www.server-world.info/en/note?os=Ubuntu_24.04&p=realmd
- https://ubuntu.com/server/docs/how-to-set-up-sssd-with-active-directory
