# Docker Compose

Docker Compose is a tool to simplify management of Docker containers. It is particularly useful in multiple container deployment.

## Docker Compose Commands

The executable binary, **docker-compose** is used to manage containers. By default, the command reads a docker file (i.e. docker-compose.yml) file that contains the definition of container's environment. This file uses the [Compose file format](https://compose-spec.io/).

The following are commonly used docker-compose commands.

### Starting Containers

Use the following command to start containers.

```bash
sudo docker-compose docker-compose.yml up -d
```

### Stopping Containers

Use the following to stop containers.

```bash
sudo docker-compose docker-compose.yml stop
```

### Stop and Remove Containers

Use the following to stop and remove containers.

```bash
sudo docker-compose docker-compose.yml down
```

### List Containers

Use the following list running containers.

```bash
sudo docker-compose docker-compose.yml ps
```

### List Containers

Use the following list running compose projects.

```bash
sudo docker-compose docker-compose.yml ls
```

### Update Docker Images

Use the following to update underlying docker images of containers defined in a docker-compose file.

First stop and remove the running containers,

```bash
sudo docker-compose docker-compose.yml down
```

Pull the latest images,

```bash
sudo docker-compose docker-compose.yml pull
```

Recreate and start container services,

```bash
    sudo docker-compose up --force-recreate --build -d
```


