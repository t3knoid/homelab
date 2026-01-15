---
title: "NFS Mount Troubleshooting Runbook"
---

# 🧭 NFS Mount Troubleshooting Runbook

Use this flow **top to bottom**. Stop once the issue is resolved.

---

## 🔴 START — NFS mount issue reported

⬇️

---

## ❓ Is the mount visible?

{% raw %}
```bash
ls <mount_point>
```
{% endraw %}

### ❌ NO — Mount not present

⬇️

### 🌐 Check NFS server reachability

{% raw %}
```bash
ping <nfs-server>
showmount -e <nfs-server>
```
{% endraw %}

❌ Fails → **Network / server issue**
✅ Works → Continue

⬇️

### 🔀 Determine mount type

#### autofs

{% raw %}
```bash
systemctl status autofs
journalctl -u autofs -f
cat /etc/auto.nfs
```
{% endraw %}

#### fstab

{% raw %}
```bash
grep <mount_point> /etc/fstab
mount -a
```
{% endraw %}

❌ Errors → **Fix configuration & retry**
✅ No errors → Continue

⬇️

---

## ❓ Is the mount present but inaccessible?

{% raw %}
```bash
ls <mount_point>
```
{% endraw %}

### ❌ Permission denied

⬇️

### 🔐 Check permissions & identity

{% raw %}
```bash
ls -ln <mount_point>
```
{% endraw %}

On NFS server:

{% raw %}
```bash
exportfs -v
```
{% endraw %}

✔ Fix UID/GID mismatch or export rules
⬇️ Retry access

---

## ❓ Is access slow or hanging?

### 🐌 YES — Timeouts or freezes

⬇️

### 🕒 Tune NFS options

Recommended:

{% raw %}
```yaml
rw,hard,proto=tcp,timeo=1200,retrans=5
```
{% endraw %}

Check:

* Network latency
* NFS server load
* Avoid `soft` mounts

⬇️ Retry access

---

## ❓ Unable to unmount?

{% raw %}
```bash
umount <mount_point>
```
{% endraw %}

### ❌ “Device or resource busy”

⬇️

### 🔍 Find open files

{% raw %}
```bash
lsof | grep <mount_point>
fuser -m <mount_point>
```
{% endraw %}

autofs only:

{% raw %}
```bash
lsof | grep /nfs/<mount_name>
```
{% endraw %}

⚠️ Last resort:

{% raw %}
```bash
umount -l <mount_point>
```
{% endraw %}

---

## ❓ Changes not persisting after reboot?

⬇️

### 🔄 Verify configuration source

#### fstab

{% raw %}
```bash
grep <mount_point> /etc/fstab
```
{% endraw %}

#### autofs

{% raw %}
```bash
cat /etc/auto.master
cat /etc/auto.nfs
systemctl restart autofs
```
{% endraw %}

⬇️ Reboot test if required

---

## ❓ Service or mount command fails?

⬇️

### 🚫 Debug directly

#### autofs

{% raw %}
```bash
autofs -f
journalctl -xe
```
{% endraw %}

#### fstab

{% raw %}
```bash
mount -av
dmesg | tail
```
{% endraw %}

---

## ✅ END — Issue resolved

If unresolved:

* Check kernel logs
* Validate NFS server health
* Escalate with logs attached

---

## 🧠 Operator Notes

* Prefer **autofs** for many or non-critical mounts
* Avoid boot-blocking mounts when possible
* Keep UID/GID consistent across environments
* Monitor active mounts:

{% raw %}
```bash
grep nfs /proc/mounts
```
{% endraw %}

