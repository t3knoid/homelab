---
title: "LazyLibrarian"
---

# 📚 LazyLibrarian

LazyLibrarian is an ebook library automation service. It tracks authors and wanted books, searches configured Newznab indexers for releases, and sends matching downloads to SABnzbd. Completed downloads are placed in the shared book library.

## 🐳 Deployment

LazyLibrarian runs in a LinuxServer [Docker](docker.md) container on the `books-0` VM, alongside [Calibre](calibre.md) and [Calibre-Web](calibre-web.md). Deployment and configuration are managed through [Ansible](ansible.md).

## 💾 Library & Downloads

The book library on [TrueNAS](truenas.md) is mounted in the container at `/books`. Completed downloads are mounted at `/downloads`. LazyLibrarian’s configuration is persisted at `/config/lazylibrarian`.

## 📥 Indexers & Download Client

LazyLibrarian is configured to search Nzb.su, Nzbgeek, and Nzbplanet. It sends downloads to [SABnzbd](sabnzbd.md) using the `ebooks` category.

## 🌐 Web Access & Authentication

The web interface is available at https://lazy.refol.us through the homelab reverse proxy, with [Microsoft Entra ID](microsoft_entra_id.md) authentication configured. LazyLibrarian’s application settings also specify form-based authentication.

## 🤖 Related Services

LazyLibrarian shares the book storage with Calibre and Calibre-Web. Its Ansible configuration also specifies a Calibre server endpoint at `http://localhost:8081`.

👉 See: [Deploy LazyLibrarian Runbook](deploy_lazylibrarian_runbook.md)
