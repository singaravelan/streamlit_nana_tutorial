# Harbor Private Container Registry & Pipeline Integration Plan

## Goal
Install Harbor container registry locally via Docker Compose, configure a private repository (`mlops-lab`), update Jenkins to push versioned Docker images to Harbor, and update production deployment to pull images directly from Harbor.

---

## 🏗️ Target Architecture

```
[Developer Push] ➔ [Jenkins CI/CD Pipeline]
                          │
                          ├─► 1. Run Python Tests (python:3.11-slim)
                          ├─► 2. Build Docker Image (streamlit-app:latest)
                          ├─► 3. Tag & Push Image ──► [Harbor Registry (localhost:8082)]
                          │                                     │
                          └─► 4. Trigger Deploy ◄───────────────┘
                                  (Pull image from Harbor & run in production_env/)
```

---

## 📋 Implementation Steps

### Step 1: Download & Install Harbor Registry Locally
1. Download official Harbor offline installer release tarball.
2. Extract tarball to `~/harbor`.
3. Configure `harbor.yml`:
   - `hostname`: `localhost`
   - `http.port`: `8082` (to avoid port 8080 collision with Jenkins and 8501 with Streamlit)
   - `harbor_admin_password`: `Harbor12345`
4. Run `./install.sh` to launch Harbor microservices (registry, core, portal, redis, db).

---

### Step 2: Configure Harbor UI & Project
1. Open Harbor Web Portal at `http://localhost:8082`.
2. Log in with `admin` / `Harbor12345`.
3. Create a new project:
   - **Project Name**: `mlops-lab`
   - **Access**: Public / Private

---

### Step 3: Configure Docker Insecure Registry Access
Because local Harbor uses HTTP (port 8082) without SSL certificates:
Add `"insecure-registries": ["localhost:8082"]` to Docker Desktop settings (`daemon.json`).

---

### Step 4: Create Production Deployment Configuration (`docker-compose.prod.yml`)
Create a dedicated `production_env/docker-compose.prod.yml` that pulls the compiled image strictly from Harbor:

```yaml
name: streamlit_prod

services:
  streamlit-prod:
    image: localhost:8082/mlops-lab/streamlit-app:latest
    container_name: streamlit-prod
    ports:
      - "8502:8501" # Runs production app on port 8502
    environment:
      - MONGO_HOST=mongodb
      - MONGO_PORT=27017
      - MONGO_USERNAME=admin
      - MONGO_PASSWORD=password
    networks:
      - mlops-network

networks:
  mlops-network:
    name: streamlit_nana_tutorial_mlops-network
    external: true
```

---

### Step 5: Update `Jenkinsfile` for Harbor Push & Production Deploy
Update `Jenkinsfile` with new registry stages:

1. **Stage: Push to Harbor Registry**:
   ```groovy
   sh 'docker login localhost:8082 -u admin -p Harbor12345'
   sh 'docker tag streamlit-app:latest localhost:8082/mlops-lab/streamlit-app:latest'
   sh 'docker push localhost:8082/mlops-lab/streamlit-app:latest'
   ```

2. **Stage: Deploy Production App**:
   ```groovy
   sh 'docker compose -f production_env/docker-compose.prod.yml up -d'
   ```

---

## 🧪 Verification Plan

1. **Harbor Verification**: Inspect `http://localhost:8082` to confirm `mlops-lab/streamlit-app:latest` artifact appears in the registry.
2. **Deployment Verification**: Visit `http://localhost:8502` to confirm the production app runs cleanly from the Harbor image.
