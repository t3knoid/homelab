# 🐳 Docker Command Cheat Sheet

## **1. Images**

* **List all images**

```bash
docker images
```

* **Pull an image from Docker Hub**

```bash
docker pull <image_name>:<tag>
```

* **Build an image from a Dockerfile**

```bash
docker build -t <image_name>:<tag> .
```

* **Remove an image**

```bash
docker rmi <image_name>:<tag>
```

---

## **2. Containers**

* **List running containers**

```bash
docker ps
```

* **List all containers** (running + stopped)

```bash
docker ps -a
```

* **Run a container**

```bash
docker run -d --name <container_name> -p <host_port>:<container_port> <image_name>:<tag>
```

* **Start a stopped container**

```bash
docker start <container_name>
```

* **Stop a running container**

```bash
docker stop <container_name>
```

* **Restart a container**

```bash
docker restart <container_name>
```

* **Remove a container**

```bash
docker rm <container_name>
```

---

## **3. Logs & Stats**

* **View logs of a container**

```bash
docker logs <container_name>
```

* **Follow logs in real-time**

```bash
docker logs -f <container_name>
```

* **View resource usage of running containers**

```bash
docker stats
```

---

## **4. Docker Compose**

* **Start containers defined in docker-compose.yml**

```bash
docker-compose up -d
```

* **Stop containers**

```bash
docker-compose down
```

* **Rebuild and restart containers**

```bash
docker-compose up -d --build
```

* **View container logs**

```bash
docker-compose logs -f
```

---

## **5. Volumes**

* **List volumes**

```bash
docker volume ls
```

* **Inspect a volume**

```bash
docker volume inspect <volume_name>
```

* **Remove a volume**

```bash
docker volume rm <volume_name>
```

---

## **6. Networks**

* **List networks**

```bash
docker network ls
```

* **Inspect a network**

```bash
docker network inspect <network_name>
```

* **Remove a network**

```bash
docker network rm <network_name>
```

---

## **7. Cleanup**

* **Remove unused containers, networks, and images**

```bash
docker system prune
```

* **Remove unused Docker images**

```bash
docker image prune -a
```

* **Remove stopped containers**

```bash
docker container prune
```

