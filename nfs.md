---
title: "NFS"
---

# 📁 NFS
Network File System (NFS) is a core storage protocol used throughout the homelab to provide shared, network‑attached directories to Linux hosts and container workloads. In this environment, **NFS shares are primarily served by a [TrueNAS](truenas.md) system**, which exposes datasets for media libraries, backups, and application data.

This page documents how NFS works in the context of Ubuntu, how it is mounted, and the two supported mounting strategies implemented in the platform: **Autofs** and **fstab‑based static mounts**.

It also explains the strengths and weaknesses of each approach, including real‑world behavior observed in the homelab (e.g., Plex not consistently seeing an Autofs‑mounted photos directory).

For implementation details, see:  
- **[Contributor Guide to Mounting Disks in Linux Using Ansible](contributor_guide_to_mounting_disks_in_linux_using_ansible.md)**  
- **[Contributor Guide on Creating Autofs Mounts Using Ansible](contributor_guide_on_creating_autofs_mounts_using_ansible.md)**

---

## 🧭 Purpose of This Page  
This page provides:

- A practical overview of NFS on Linux/Ubuntu  
- How NFS mounts are managed using Ansible  
- A comparison of **Autofs** vs **fstab** mounts  
- Guidance on when to use each method  
- Notes on Plex and other applications that behave differently depending on mount type  
- Links to contributor guides for implementing mounts in Ansible  

---

## 📡 What Is NFS?  
NFS (Network File System) is a distributed filesystem protocol that allows Linux hosts to mount remote directories as if they were local. In the homelab, **TrueNAS is the primary NFS server**, exposing datasets for:

- Media libraries (movies, TV, music, photos)  
- Application data  
- Backups  
- Shared working directories  

TrueNAS provides stable, POSIX‑compliant NFS exports that integrate cleanly with Ubuntu clients.

### Key characteristics  
- Stateless protocol  
- Lightweight and fast  
- Ideal for media libraries, backups, and shared data  
- Native support in Linux kernels  
- Mountable via Autofs or `/etc/fstab`  

---

## 🐧 NFS on Ubuntu  
Ubuntu includes first‑class support for NFS through the `nfs-common` package, which provides:

- The `mount.nfs` helper  
- NFSv3 and NFSv4 support  
- Locking daemons  
- Client‑side caching  

Most NFS mounts in the homelab use:

- **NFSv3** for compatibility with media applications  
- **Hard mounts** with large read/write buffers  
- **TCP transport** for reliability  
- **sec=sys** authentication  

---

# 🧩 Mounting NFS Shares in the Platform  
The platform supports two mounting strategies, each implemented as an Ansible role:

### 1. **Autofs** (on‑demand, dynamic mounts)  
### 2. **fstab** (static, always‑mounted entries)

Both are valid, but they behave differently and are suited to different workloads.

---

## 🔀 Autofs Mounts  
Autofs mounts directories **on demand** when they are accessed and unmounts them after a period of inactivity.

### ✔️ Strengths  
- **Resilient to NAS restarts**  
  If TrueNAS goes offline, Autofs simply remounts when accessed again.  
- **No boot‑time delays**  
  The system doesn’t hang waiting for NFS during boot.  
- **Ideal for infrequently accessed data**  
  Great for large media libraries or archival directories.  
- **Reduces stale mount issues**  
  Because mounts are not persistent.

### ❌ Weaknesses  
- **Some applications don’t handle on‑demand mounts well**  
  Plex is the most common offender.  
- **Directories may appear empty if the mount hasn’t triggered yet**  
  GUI apps and containerized workloads sometimes read before Autofs mounts.  
- **Inconsistent behavior with certain workloads**  
  Plex failed to consistently see the `/photos` Autofs mount, even though `/movies`, `/tvshows`, and `/music` worked fine.  
  Plex scans image libraries differently than video libraries, and the access pattern may not reliably trigger Autofs.  
- **Harder to debug**  
  Because mounts appear and disappear dynamically.

### When to use Autofs  
- Media libraries accessed by apps that handle dynamic mounts well  
- Backup directories  
- Large, infrequently accessed datasets  
- Hosts that must remain boot‑fast and resilient to NAS outages  

---

## 📌 fstab Mounts  
`/etc/fstab` mounts are **static**, **persistent**, and **always mounted** once the system is up.

### ✔️ Strengths  
- **Always available**  
  Applications like Plex, Docker containers, and system services see the directory immediately.  
- **Predictable behavior**  
  No on‑demand logic; the mount is simply there.  
- **Better compatibility with applications that scan directories**  
  Plex photo libraries, in particular, behave more reliably with static mounts.  
- **Easier to debug**  
  If it’s mounted, it’s mounted.

### ❌ Weaknesses  
- **Boot delays if TrueNAS is unavailable**  
  Unless `nofail` or `x-systemd.automount` is used.  
- **Stale mounts**  
  If TrueNAS restarts, the mount may hang until manually remounted.  
- **Less flexible**  
  Everything is mounted whether needed or not.

### When to use fstab  
- Plex photo libraries  
- Docker bind mounts  
- Any workload that expects the directory to always exist  
- High‑availability or latency‑sensitive services  
- Hosts where predictable mount state is more important than boot speed  

---

# 🧭 Choosing Between Autofs and fstab  
A simple decision guide:

| Requirement | Autofs | fstab |
|------------|--------|-------|
| Must be always available | ❌ | ✔️ |
| Plex photo libraries | ❌ | ✔️ |
| Plex video libraries | ✔️ | ✔️ |
| Resilient to TrueNAS restarts | ✔️ | ❌ |
| Fast boot | ✔️ | ❌ (unless tuned) |
| Infrequent access | ✔️ | ❌ |
| Docker bind mounts | ❌ | ✔️ |
| Simple debugging | ❌ | ✔️ |

---

## 🛠 Ansible Integration  
The platform provides two contributor‑ready roles:

- **[Contributor Guide to Mounting Disks in Linux Using Ansible](contributor_guide_to_mounting_disks_in_linux_using_ansible.md)** - Covers the fstab‑based static mount role.
- **[Contributor Guide on Creating Autofs Mounts Using Ansible](contributor_guide_on_creating_autofs_mounts_using_ansible.md)** -Covers the Autofs role and map file generation.

## 🩺 Troubleshooting (autofs & fstab)

This section applies to **both automounted (`autofs`) and static (`/etc/fstab`) NFS mounts** unless otherwise noted.

---

### ❌ Mount not appearing or inaccessible

**Check basic connectivity**

{% raw %}
```bash
ping <nfs-server>
showmount -e <nfs-server>
```
{% endraw %}

**autofs only**

{% raw %}
```bash
systemctl status autofs
journalctl -u autofs -f
cat /etc/auto.nfs
```
{% endraw %}

**fstab only**

{% raw %}
```bash
grep <mount_point> /etc/fstab
mount -a
```
{% endraw %}

---

### ⛔ “Device or resource busy” / unmount failures

Usually caused by open files or active processes.

{% raw %}
```bash
lsof | grep <mount_point>
fuser -m <mount_point>
```
{% endraw %}

To identify *all* open files:

{% raw %}
```bash
lsof +D <mount_point>
```
{% endraw %}

> ⚠️ Forcibly unmounting active NFS mounts can cause data loss.

---

### 🔐 “Permission denied” errors

Common causes:

* Incorrect NFS export permissions
* UID/GID mismatches between client and server
* Client IP not allowed in export

**Verify exports on server**

{% raw %}
```bash
exportfs -v
```
{% endraw %}

**Check ownership on client**

{% raw %}
```bash
ls -ln <mount_point>
```
{% endraw %}

---

### 🕒 Timeouts, slow mounts, or hanging I/O

Often network-related or due to aggressive timeout settings.

**Recommended NFS options**

{% raw %}
```yaml
rw,hard,proto=tcp,timeo=1200,retrans=5
```
{% endraw %}

**Troubleshooting steps**

* Increase `timeo` (value is in deciseconds)
* Verify network stability
* Monitor NFS server load
* Avoid `soft` mounts in production

---

### 🔄 Changes not persisting after reboot

**fstab**

* Confirm entry exists and is correct:

  ```bash
  grep <mount_point> /etc/fstab
  ```

**autofs**

* Ensure configuration is in `/etc/auto.master` and `/etc/auto.nfs`
* Restart service after changes:

  ```bash
  systemctl restart autofs
  ```

---

### 🔍 Mount not unmounting (autofs)

Autofs will not unmount if files are in use.

{% raw %}
```bash
lsof | grep /nfs/<mount_name>
```
{% endraw %}

Force a lazy unmount if necessary:

{% raw %}
```bash
sudo umount -l /nfs/<mount_name>
```
{% endraw %}

---

### 🚫 Service or mount command failures

**autofs**

{% raw %}
```bash
autofs -f
journalctl -xe
```
{% endraw %}

**fstab**

{% raw %}
```bash
mount -av
dmesg | tail
```
{% endraw %}

---

## 🧭 Best Practices

### 🔹 Universal (applies to **autofs** and **fstab**)

* **Use meaningful mount points**
  Example: `/nfs/media`, `/nfs/backups`, `/local/backup`

* **Choose reliable mount options**
  Balance performance and stability; avoid experimental flags in production.

* **Prefer `hard` mounts for data integrity**
  Prevents silent data corruption on transient failures.

* **Keep UID/GID mappings consistent**
  Especially critical for shared or multi-user environments.

* **Use `relatime` on modern systems**
  Reduces unnecessary metadata writes while remaining POSIX-friendly.

* **Test NFS connectivity before deployment**

  ```bash
  ping <nfs-server>
  showmount -e <nfs-server>
  ```

* **Document mount purpose and ownership**
  Store intent in `group_vars` / `host_vars` for maintainability.

* **Periodically verify mount health**

  ```bash
  grep nfs /proc/mounts
  ```

---

### 🔁 autofs-Specific Best Practices

* **Prefer autofs for non-critical or numerous mounts**
  Ideal for media libraries, shared resources, and large mount sets.

* **Avoid mounting at boot**
  Autofs prevents boot delays if the NFS server is unavailable.

* **Ensure mounts are idle-unmounted**
  Watch for lingering file handles:

  ```bash
  lsof | grep /nfs
  ```

* **Restart autofs after configuration changes**

  ```bash
  systemctl restart autofs
  ```

---

### 📌 fstab-Specific Best Practices

* **Avoid boot-blocking mounts unless required**
  Boot-time NFS failures can hang the system.

* **Use `nofail` for optional mounts**

  ```text
  nofail
  ```

* **Validate entries after changes**

  ```bash
  mount -a
  ```

* **Reserve fstab for critical storage**
  Databases, system paths, and required application data.

---

### ✅ Recommended Defaults

{% raw %}
```text
rw,hard,relatime,proto=tcp,timeo=600,retrans=2
```
{% endraw %}
