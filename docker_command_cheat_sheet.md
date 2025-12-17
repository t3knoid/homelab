---
title: "Docker Command Cheat Sheet"
---

# 🐳 Docker Command Cheat Sheet

## **1. Images**

* **List all images**

{% raw %}
```bash
docker images
```
{% endraw %}

* **Pull an image from Docker Hub**

{% raw %}
```bash
docker pull <image_name>:<tag>
```
{% endraw %}

* **Build an image from a Dockerfile**

{% raw %}
```bash
docker build -t <image_name>:<tag> .
```
{% endraw %}

* **Remove an image**

{% raw %}
```bash
docker rmi <image_name>:<tag>
```
{% endraw %}

---

## **2. Containers**

* **List running containers**

{% raw %}
```bash
docker ps
```
{% endraw %}

* **List all containers** (running + stopped)

{% raw %}
```bash
docker ps -a
```
{% endraw %}

* **Run a container**

{% raw %}
```bash
docker run -d --name <container_name> -p <host_port>:<container_port> <image_name>:<tag>
```
{% endraw %}

* **Start a stopped container**

{% raw %}
```bash
docker start <container_name>
```
{% endraw %}

* **Stop a running container**

{% raw %}
```bash
docker stop <container_name>
```
{% endraw %}

* **Restart a container**

{% raw %}
```bash
docker restart <container_name>
```
{% endraw %}

* **Remove a container**

{% raw %}
```bash
docker rm <container_name>
```
{% endraw %}

---

## **3. Logs & Stats**

* **View logs of a container**

{% raw %}
```bash
docker logs <container_name>
```
{% endraw %}

* **Follow logs in real-time**

{% raw %}
```bash
docker logs -f <container_name>
```
{% endraw %}

* **View resource usage of running containers**

{% raw %}
```bash
docker stats
```
{% endraw %}

---

## **4. Docker Compose**

* **Start containers defined in docker-compose.yml**

{% raw %}
```bash
docker-compose up -d
```
{% endraw %}

* **Stop containers**

{% raw %}
```bash
docker-compose down
```
{% endraw %}

* **Rebuild and restart containers**

{% raw %}
```bash
docker-compose up -d --build
```
{% endraw %}

* **View container logs**

{% raw %}
```bash
docker-compose logs -f
```
{% endraw %}

---

## **5. Volumes**

* **List volumes**

{% raw %}
```bash
docker volume ls
```
{% endraw %}

* **Inspect a volume**

{% raw %}
```bash
docker volume inspect <volume_name>
```
{% endraw %}

* **Remove a volume**

{% raw %}
```bash
docker volume rm <volume_name>
```
{% endraw %}

---

## **6. Networks**

* **List networks**

{% raw %}
```bash
docker network ls
```
{% endraw %}

* **Inspect a network**

{% raw %}
```bash
docker network inspect <network_name>
```
{% endraw %}

* **Remove a network**

{% raw %}
```bash
docker network rm <network_name>
```
{% endraw %}

---

## **7. Cleanup**

* **Remove unused containers, networks, and images**

{% raw %}
```bash
docker system prune
```
{% endraw %}

* **Remove unused Docker images**

{% raw %}
```bash
docker image prune -a
```
{% endraw %}

* **Remove stopped containers**

{% raw %}
```bash
docker container prune
```
{% endraw %}

