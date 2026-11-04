---
title: "Calibre"
---

# 📚 Calibre

Calibre is an ebook library management application for organizing an ebook collection and managing book metadata. In this homelab, its content server provides browser access to the library at `catalog.refol.us`.

Calibre is separate from [Calibre-Web](calibre-web.md), which provides the web interface at https://books.refol.us, and [LazyLibrarian](lazylibrarian.md), which is used for ebook automation at https://lazy.refol.us.

## 🐳 Deployment

Calibre runs in a LinuxServer [Docker](docker.md) container on the `books-0` VM. Deployment and configuration are managed through [Ansible](ansible.md) using `deploy_calibre.yml`.

## 💾 Library & Storage

The ebook library is stored on [TrueNAS](truenas.md) and mounted in the container at `/books`. Completed downloads are mounted at `/downloads`. Calibre’s configuration is persisted at `/config/calibre`.

## 🌐 Web Access & Authentication

The Calibre content server is available at https://catalog.refol.us through the homelab reverse proxy. The proxy uses [Microsoft Entra ID](microsoft_entra_id.md) authentication. It forwards requests to Calibre on port `8081`.

## 🤖 Related Services

Calibre shares the `books-0` VM and book storage with [Calibre-Web](calibre-web.md) and [LazyLibrarian](lazylibrarian.md). Calibre-Web provides a separate library browsing interface, while LazyLibrarian handles ebook automation.

👉 See: [Deploy Calibre Runbook](deploy_calibre_runbook.md)