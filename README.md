# Build and Deployment Instructions

This guide provides step-by-step instructions for building, running, and deploying the Turf Booking microservices platform locally and to AWS EC2.

---

## 🛠️ Prerequisites

* **Local Environment**: Windows 10/11, macOS, or Linux with [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed.
* **AWS Cloud Environment**: An active AWS account with access to provision an EC2 instance (`Ubuntu 24.04 LTS`, recommended instance type: `t3.medium`).

---

## 💻 1. Local Build and Execution

### Step 1: Clone the Repository & Navigate to Directory
```bash
git clone https://github.com/your-org/turf-booking-platform.git
cd turf-booking-platform
```

### Step 2: Verify Configuration Files
Ensure that `prometheus.yml` exists in the root folder alongside `docker-compose.yaml`.

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'turf-service'
    static_configs:
      - targets: ['turf-service:8001']

  - job_name: 'booking-service'
    static_configs:
      - targets: ['booking-service:8002']

  - job_name: 'payment-service'
    static_configs:
      - targets: ['payment-service:8003']

  - job_name: 'notification-service'
    static_configs:
      - targets: ['notification-service:8004']
```

### Step 3: Build and Launch Containers
Clean up any existing containers/volumes and start all services in detached mode:
```bash
docker compose down -v
docker compose up --build -d
```

### Step 4: Verify Local Health
Check that all 6 containers (`turf-service`, `booking-service`, `payment-service`, `notification-service`, `prometheus`, `grafana`) are running:
```bash
docker compose ps
```

---

## ☁️ 2. AWS EC2 Production Deployment

### Step 1: Launch an AWS EC2 Instance
1. Open the **AWS Management Console** and navigate to **EC2**.
2. Click **Launch Instance**:
   * **Name**: `turf-booking-production`
   * **AMI**: Ubuntu 24.04 LTS
   * **Instance Type**: `t3.medium` (2 vCPU, 4 GiB Memory recommended)
   * **Key Pair**: Select your SSH `.pem` key pair.

### Step 2: Configure AWS Security Group Inbound Rules
Under **Security Groups > Edit Inbound Rules**, add the following inbound access rules:

| Protocol | Port Range | Source | Description |
| :--- | :--- | :--- | :--- |
| SSH | `22` | `0.0.0.0/0` (or your IP) | Remote SSH Access |
| Custom TCP | `8001 - 8004` | `0.0.0.0/0` | Microservice APIs |
| Custom TCP | `9090` | `0.0.0.0/0` | Prometheus Dashboard |
| Custom TCP | `3000` | `0.0.0.0/0` | Grafana Dashboard |

### Step 3: Connect to EC2 and Install Docker
SSH into your EC2 instance:
```bash
ssh -i /path/to/your-key.pem ubuntu@<YOUR_EC2_PUBLIC_IP>
```

Execute the following script to set up Docker Engine and the Docker Compose plugin:
```bash
# Update system and install prerequisites
sudo apt-get update
sudo apt-get install -y ca-certificates curl

# Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker packages
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Grant docker permissions to current user
sudo usermod -aG docker $USER
newgrp docker
```

### Step 4: Transfer Project Files and Deploy Stack
1. Clone or copy your project files onto the EC2 server:
   ```bash
   git clone https://github.com/your-org/turf-booking-platform.git
   cd turf-booking-platform
   ```
2. Build and launch the container stack:
   ```bash
   docker compose up --build -d
   ```
3. Confirm container operational status:
   ```bash
   docker compose ps
   ```

---

## 🌐 Endpoint Summary

Replace `<HOST_IP>` with `localhost` for local deployment or your `<EC2_PUBLIC_IP>` for cloud deployment:

| Service | Port | Endpoint |
| :--- | :--- | :--- |
| **Turf Service API** | `8001` | `http://<HOST_IP>:8001/docs` |
| **Booking Service API** | `8002` | `http://<HOST_IP>:8002/docs` |
| **Payment Service API** | `8003` | `http://<HOST_IP>:8003/docs` |
| **Notification Service API** | `8004` | `http://<HOST_IP>:8004/docs` |
| **Prometheus Dashboard** | `9090` | `http://<HOST_IP>:9090` |
| **Grafana Dashboard** | `3000` | `http://<HOST_IP>:3000` *(Login: admin / admin)* |

---

## 🔧 Useful Deployment Operations

* **View live logs across all containers**:
  ```bash
  docker compose logs -f
  ```
* **View logs for a single service**:
  ```bash
  docker compose logs -f turf-service
  ```
* **Restart the complete stack**:
  ```bash
  docker compose restart
  ```
* **Full cleanup and rebuild**:
  ```bash
  docker compose down -v
  docker compose up --build -d
  ```