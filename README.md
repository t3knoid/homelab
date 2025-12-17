# 🏠 homelab — Markdown Mirror

⚠️ Important: other than this `README.md`, the Markdown files in this repository must NOT be edited by hand.

- ⚙️ These Markdown files are automatically generated from an Ansible playbook. Any manual edits to the generated Markdown will be overwritten the next time the playbook runs.
- ⤴️ To (re)generate the Markdown files locally, run:

```bash
ansible-playbook -i inventory/redmine/inventory.ini -k playbooks/redmine/mirror_wiki.yml
```

- 🌐 This repository is a one-way mirror of the wiki pages from: 📄➡️📄

	https://homelab.refol.us/projects/home-lab/wiki
- 🔗 Playbook source (generator): https://github.com/t3knoid/ansible/blob/main/playbooks/redmine/mirror_wiki.yml

**GitHub Pages**
- The repository is published as a static site at: https://t3knoid.github.io/homelab/ 🚀

The GitHub Actions workflow that builds and deploys the site is at
[.github/workflows/static.yml](.github/workflows/static.yml). In short, the workflow:

- 🔁 Runs on pushes to `main` and via manual dispatch.
- ✅ Checks out the repository (`actions/checkout`).
- 💎 Sets up Ruby and installs Jekyll and Bundler-managed dependencies.
- 🛠️ Builds the Jekyll site into the `./_site` directory using `bundle exec jekyll build`.
- 📤 Uploads the generated `_site` artifact and deploys it to GitHub Pages.

Because the site is rendered from the repository's Markdown, the canonical source of truth for the content is the Ansible playbook that generates the Markdown (see the command above). If you want to propose content changes, update the wiki at the upstream source or modify the playbook/process that generates these files.

✉️ If you need help running the playbook or understanding the workflow, open an issue or ask the repository maintainers.
