# LDAP

User: ldap_bind_user
DN: "CN=LDAP Bind User,OU=Service Accounts,DC=refol,DC=us"

## Testing LDAP Using python-ldap library

Use the following code to test LDAP connection. Install [python-ldap](https://www.python-ldap.org/en/python-ldap-3.4.3/installing.html#installing) before proceeding.

```python
import ldap
import logging

# Enable logging for debugging
logging.basicConfig(level=logging.DEBUG)

# LDAP server details
ldap_server = "ldap://192.168.2.251"
bind_dn = "CN=LDAP Bind User,OU=Service Accounts,DC=refol,DC=us"
password = "mysecurepassword"
search_base = "CN=Users,DC=refol,DC=us"
search_filter = "(sAMAccountName=frank)"  # Replace with your search filter

try:
    # Initialize LDAP connection
    ldap_connection = ldap.initialize(ldap_server)
    ldap_connection.set_option(ldap.OPT_REFERRALS, 0)  # Important for AD

    # Bind/Authenticate with the server
    ldap_connection.simple_bind_s(bind_dn, password)
    print("LDAP bind successful")

    # Perform an LDAP search
    result = ldap_connection.search_s(search_base, ldap.SCOPE_SUBTREE, search_filter)
    print("LDAP search result:", result)

except ldap.INVALID_CREDENTIALS:
    print("Invalid credentials")
except ldap.LDAPError as e:
    print("LDAP error:", e)
finally:
    # Unbind the connection
    ldap_connection.unbind_s()
```

## References

- https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2008-R2-and-2008/cc816778(v=ws.10)?redirectedfrom=MSDN
- https://learn.microsoft.com/en-us/powershell/module/servermanager/install-windowsfeature?view=windowsserver2022-ps
- https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2008-R2-and-2008/cc816774(v=ws.10)?redirectedfrom=MSDN
- 