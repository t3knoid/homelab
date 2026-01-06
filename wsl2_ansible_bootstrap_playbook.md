---
title: "WSL2 Ansible Bootstrap Playbook"
---

# ✅ **WSL2 Ansible Bootstrap Playbook**

{% raw %}
```
---
- name: Bootstrap WSL2 Ubuntu 24.04 as an Ansible Control Node
  hosts: localhost
  connection: local
  become: yes

  vars:
    ansible_venv_path: "{{ ansible_env.HOME }}/ansible/.venv"
    ansible_workspace: "{{ ansible_env.HOME }}/ansible"
    ansible_requirements_url: ""   # Optional: URL to your requirements.txt
    ansible_repo_url: ""           # Optional: Git repo to clone
    ansible_repo_dest: "{{ ansible_env.HOME }}/projects/ansible"

  tasks:

    - name: Update apt cache
      apt:
        update_cache: yes
        cache_valid_time: 3600

    - name: Install base packages
      apt:
        name:
          - python3
          - python3-venv
          - python3-pip
          - python3-dev
          - git
          - openssh-client
          - openssh-server
          - build-essential
        state: present

    - name: Ensure SSH service is enabled
      systemd:
        name: ssh
        enabled: yes
        state: started

    - name: Create Ansible workspace directory
      file:
        path: "{{ ansible_workspace }}"
        state: directory
        mode: "0755"
        owner: "{{ ansible_user_id }}"
        group: "{{ ansible_user_gid }}"

    - name: Create Python virtual environment
      command: python3 -m venv "{{ ansible_venv_path }}"
      args:
        creates: "{{ ansible_venv_path }}/bin/activate"

    - name: Install pip upgrade inside venv
      pip:
        name: pip
        state: latest
        virtualenv: "{{ ansible_venv_path }}"

    - name: Download requirements.txt (optional)
      get_url:
        url: "{{ ansible_requirements_url }}"
        dest: "{{ ansible_workspace }}/requirements.txt"
      when: ansible_requirements_url != ""

    - name: Install Python requirements inside venv
      pip:
        requirements: "{{ ansible_workspace }}/requirements.txt"
        virtualenv: "{{ ansible_venv_path }}"
      when: ansible_requirements_url != "" or
            lookup('ansible.builtin.fileglob', ansible_workspace + '/requirements.txt', errors='ignore') | length > 0

    - name: Clone Ansible repo (optional)
      git:
        repo: "{{ ansible_repo_url }}"
        dest: "{{ ansible_repo_dest }}"
        version: main
      when: ansible_repo_url != ""

    - name: Create ~/.ssh directory
      file:
        path: "{{ ansible_env.HOME }}/.ssh"
        state: directory
        mode: "0700"

    - name: Ensure SSH key exists
      openssh_keypair:
        path: "{{ ansible_env.HOME }}/.ssh/id_rsa"
        type: rsa
        size: 4096
        state: present
        mode: "0600"

    - name: Display summary
      debug:
        msg:
          - "WSL2 Ansible control node bootstrap complete."
          - "Virtualenv: {{ ansible_venv_path }}"
          - "Workspace: {{ ansible_workspace }}"
          - "SSH key: {{ ansible_env.HOME }}/.ssh/id_rsa"
```
{% endraw %}

---

# 🧩 **What This Playbook Does**

### ✔ Installs all required packages  
- Python, pip, venv  
- Git  
- OpenSSH server + client  
- Build tools (needed for some Python wheels)

### ✔ Creates a clean Ansible workspace  
`~/ansible`

### ✔ Creates a Python virtual environment  
`~/ansible/.venv`

### ✔ Installs your requirements.txt  
Either from a URL or a local file.

### ✔ Optionally clones your Ansible repo  
If you set `ansible_repo_url`.

### ✔ Ensures SSH server is running  
Useful for remote access into WSL2.

### ✔ Generates SSH keys if missing  
Idempotent and safe.

