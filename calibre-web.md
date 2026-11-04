---
title: "Calibre-Web"
---

# 📚 Calibre-Web

Calibre-Web is a web-based interface for browsing and accessing an ebook library. In this homelab, `books.refol.us` serves the Calibre-Web application on the `books-0` VM.

## 🐳 Deployment

Calibre-Web runs in a LinuxServer [Docker](docker.md) container. It is deployed and configured through [Ansible](ansible.md).

## 💾 Library & Storage

The ebook library on [TrueNAS](truenas.md) is mounted into the container at `/books`. Completed downloads are mounted at `/downloads`. Calibre-Web’s application configuration is persisted at `/config/calibreweb`.

## 🌐 Web Access & Authentication

https://books.refol.us is routed through the homelab reverse proxy to Calibre-Web on port `8083`. The proxy has an IP allow-list configured; Entra ID authentication is not enabled for this hostname.

## 📚 Related Book Services

The `books-0` VM also hosts two separate applications:

- `catalog.refol.us` routes to the [Calibre](calibre.md) content server.
- `lazy.refol.us` routes to [LazyLibrarian](lazylibrarian.md), which provides ebook library automation.

These services share the VM and NAS book storage, but have their own hostnames and application interfaces.

## 🤖 Automation & Backups

Calibre-Web is deployed with `deploy_calibreweb.yml`. I found no Calibre-Web-specific scheduled backup or restore task configured in Semaphore.

👉 See: [Deploy Calibre-Web Runbook](deploy_calibre-web_runbook.md) [Deploy Lazy Librarian Runbook](deploy_lazy_librarian_runbook.md)