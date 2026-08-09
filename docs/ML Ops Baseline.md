# MLOps Baseline Architecture & System Documentation

## Overview
This document defines the baseline local MLOps architecture built with Streamlit, MongoDB, Jenkins CI/CD, TCP Docker Cloud Agents, Harbor Private Container Registry, and dual (Dev/Prod) deployment environments.

---

## 🏗️ System Architecture Diagram

```
                                  DEVELOPER WORKSTATION
                                ┌───────────────────────┐
                                │   Developer (You)     │
                                └───────────┬───────────┘
                                            │
                                            ▼ (1. git push origin main)
                                ┌───────────────────────┐
                                │  GitHub Remote Repo   │
                                └───────────┬───────────┘
                                            │
                                            ▼ (2. Poll SCM every 2 mins)
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                               JENKINS CI/CD CONTROLLER                                  │
│                                  (http://localhost:8080)                                │
└───────────────────────────────────────────┬─────────────────────────────────────────────┘
                                            │
                                            ▼ (3. Spins up dynamic TCP Agent over port 50000)
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                        DYNAMIC DOCKER AGENT (jenkins/inbound-agent)                     │
│                        - Isolated execution environment on mlops-network                │
│                        - Executes Python Smoke & Regression Tests                       │
│                        - Builds Docker Image (`streamlit-app:latest`)                   │
└───────────┬─────────────────────────────────────────────────────────────────────────────┘
            │
            ├──────────────────────────────────────────────────────┐
            ▼ (4. Push compiled image)                             ▼ (5. Hot-reload Dev)
┌──────────────────────────────────────┐             ┌──────────────────────────────────┐
│       HARBOR PRIVATE REGISTRY        │             │      DEVELOPMENT ENVIRONMENT     │
│        (http://localhost:8082)       │             │       (http://localhost:8501)    │
│  - Artifact: mlops-lab/streamlit-app │             │   - Container: `streamlit-dev`   │
└───────────────────┬──────────────────┘             └──────────────────────────────────┘
                    │
                    ▼ (6. Pull tested image from Harbor)
┌──────────────────────────────────────┐
│        PRODUCTION ENVIRONMENT        │
│        (http://localhost:8502)       │
│   - Container: `streamlit-prod`      │
└──────────────────────────────────────┘
```

---

## 🌐 Port Mapping & Service Directory

| Service | Container Name | URL / Address | Description |
| :--- | :--- | :--- | :--- |
| **Jenkins Controller** | `jenkins` | `http://localhost:8080` | CI/CD pipeline orchestrator |
| **Jenkins Agent TCP Port**| - | `tcp://localhost:50000` | Inbound TCP agent communication |
| **Harbor Registry Portal**| `nginx` | `http://localhost:8082` | Enterprise container registry UI |
| **Streamlit Dev App** | `streamlit-dev` | `http://localhost:8501` | Live development environment |
| **Streamlit Prod App** | `streamlit-prod` | `http://localhost:8502` | Production app running Harbor image |
| **Mongo Express UI** | `mongo-express` | `http://localhost:8081` | Database administration GUI |
| **MongoDB** | `mongodb` | `localhost:27017` | Backend document database |

---

## 🔄 End-to-End Pipeline Execution Lifecycle

1. **Code Commit & Push:**
   Developer updates application code (`src/app.py`) or test suite (`tests/test_app.py`) and executes `git push origin main`.

2. **SCM Polling:**
   Jenkins Controller polls GitHub (`git@github.com:singaravelan/streamlit_nana_tutorial.git`) every 2 minutes. When changes are detected, it reads the declarative `Jenkinsfile`.

3. **Dynamic TCP Docker Agent Provisioning:**
   Jenkins uses the Docker Cloud Plugin (`unix:///var/run/docker.sock`) to spin up an ephemeral container (`jenkins/inbound-agent:alpine`) connected over TCP port 50000 on network `streamlit_nana_tutorial_mlops-network`.

4. **Isolated Automated Testing:**
   Inside the agent, `python3` and dependencies are loaded, and automated tests (`tests/test_app.py`) execute. If tests fail, the build terminates immediately, leaving production untouched.

5. **Artifact Compilation & Push:**
   Upon passing tests, Jenkins compiles the container image and pushes it to Harbor Private Registry (`localhost:8082/mlops-lab/streamlit-app:latest`).

6. **Continuous Deployment (Dual Environments):**
   - **Dev Environment (`http://localhost:8501`)**: Rebuilt and hot-reloaded automatically.
   - **Prod Environment (`http://localhost:8502`)**: Deployed via `docker-compose.prod.yml`, pulling verified images directly from Harbor.

---

## 📁 Key File Locations

- **Pipeline Script**: [`Jenkinsfile`](file:///Users/singaravelang/mlops-lab/projects/experiments/streamlit_nana_tutorial/Jenkinsfile)
- **Dev Compose File**: [`docker-compose.dev.yml`](file:///Users/singaravelang/mlops-lab/projects/experiments/streamlit_nana_tutorial/docker-compose.dev.yml)
- **Prod Compose File**: [`production_env/docker-compose.prod.yml`](file:///Users/singaravelang/mlops-lab/projects/experiments/streamlit_nana_tutorial/production_env/docker-compose.prod.yml)
- **Harbor Configuration**: [`/Users/singaravelang/mlops-lab/infrastructure/harbor/harbor.yml`](file:///Users/singaravelang/mlops-lab/infrastructure/harbor/harbor.yml)
- **Test Suite**: [`tests/test_app.py`](file:///Users/singaravelang/mlops-lab/projects/experiments/streamlit_nana_tutorial/tests/test_app.py)
