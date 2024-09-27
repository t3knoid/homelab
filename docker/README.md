# Docker

This provides details in installing Docker on Ubuntu 2024.


- Docker images, containers and volumes are located under /var/lib/docker/

## Installation

### Create a an Ubuntu 24 Container in Proxmox 

Using the Ubuntu 24.04.1 ISO installer, create an Ubuntu container inside Proxmox. Open the console after the VM has been created.

### Setup Docker's apt repository.

```bash
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```

### Install the latest Docker packages

```bash
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

## References

- https://docs.docker.com/engine/install/ubuntu/