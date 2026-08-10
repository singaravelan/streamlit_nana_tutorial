# Developer Setup Guide — Local MLOps Lab

This guide sets up the full local CI/CD lab: **Jenkins + Docker Cloud agents + Harbor registry + Streamlit app** on a single machine using Docker.

It uses the simple, socket-based approach (DevOps Journey style) — no Docker-in-Docker, no TLS certificates.

---

## 1. Architecture at a glance

| Service | URL | Notes |
| :--- | :--- | :--- |
| Jenkins | http://localhost:8081 | CI/CD controller |
| Harbor | http://localhost:8082 | Private image registry (`admin` / `Harbor12345`) |
| Streamlit Dev | http://localhost:8501 | Built and hot-reloaded by the pipeline |
| Streamlit Prod | http://localhost:8502 | Pulled from Harbor |
| Mongo Express | http://localhost:8083 | DB admin UI |
| MongoDB | localhost:27017 | Backend database |

Pipeline flow: **Checkout → Install tools → Tests → Build image → Push to Harbor → Deploy Dev → Deploy Prod**

---

## 2. Prerequisites

- Docker + Docker Compose installed and running
- Git with access to the app repository
- Harbor installer extracted (e.g. `~/harbor` or `/mnt/c/Users/<you>/harbor`)

---

## 3. Create the shared network (once)

Both Jenkins and the app containers attach to this external network.

```bash
docker network create streamlit_nana_tutorial_mlops-network
```

---

## 4. Start Harbor (registry) on port 8082

The app pushes to `localhost:8082`, so configure Harbor to serve there.

1. Edit `harbor.yml` in your Harbor install directory:
   ```yaml
   hostname: localhost
   http:
     port: 8082
   ```
2. Apply the config and start it:
   ```bash
   cd <harbor-install-dir>
   ./prepare
   docker compose up -d
   ```
3. Verify:
   ```bash
   curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8082/api/v2.0/ping   # expect 200
   ```
4. Log in at http://localhost:8082 (`admin` / `Harbor12345`) and create a project named **`mlops-lab`**
   (Projects → New Project → name `mlops-lab`). The push stage fails without it.

---

## 5. Start Jenkins

`docker-compose.jenkins.yml` runs Jenkins with the **host Docker socket mounted**, so the Docker Cloud
plugin can launch agent containers on the host daemon.

```bash
cd streamlit_nana_tutorial
docker compose -f docker-compose.jenkins.yml up -d
```

Open http://localhost:8081. If this is a fresh volume, unlock with:

```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Install suggested plugins, then install the **Docker** plugin (Manage Jenkins → Plugins → Available).

---

## 6. Configure the Docker Cloud (one-time UI step)

Manage Jenkins → Clouds → New cloud → Docker.

**Docker Cloud details**
- Name: `docker-local`
- Docker Host URI: `unix:///var/run/docker.sock`
- Server credentials: none
- Click **Test Connection** → must show a Docker version

**Docker Agent Template**
- Labels: `docker-python-agent`   (must match `agent { label ... }` in the Jenkinsfile)
- Name: `docker-python-agent`
- Docker Image: `jenkins/inbound-agent:alpine`
- Instance Capacity: `2`
- Remote File System Root: `/home/jenkins/agent`
- Connect method: **Attach Docker container**
- Container settings → **Volumes**:
  ```
  /var/run/docker.sock:/var/run/docker.sock
  ```
  This lets the agent run `docker` / `docker compose` commands.

Save.

---

## 7. Set up the TCP agent port

Manage Jenkins → Security → Agents → set to **Fixed: 50000** (already published by the compose file).

---

## 8. Create the pipeline job

1. New Item → Pipeline → name `ml_ops_lab_pipeline`.
2. Pipeline → Definition: **Pipeline script from SCM** → Git → your repo URL → branch `main` → Script Path `Jenkinsfile`.
3. (Optional) Build Triggers → Poll SCM → `H/5 * * * *` (every 5 minutes).
4. Save → **Build Now**.

---

## 9. Common errors and fixes (things that tripped us up)

| Symptom in console | Cause | Fix |
| :--- | :--- | :--- |
| `'Jenkins' doesn't have label 'docker-python-agent'` | Cloud template label doesn't match Jenkinsfile | Set template **Labels** to exactly `docker-python-agent` |
| `network jenkins-dind-net not found` | Template network doesn't exist on the daemon | Use a network that exists, or leave default bridge |
| `apk add ... Permission denied` | Agent ran as non-root | Use the socket/attach setup; ensure agent can write (root) |
| `docker API at unix:///var/run/docker.sock ... no such file` | Agent has no Docker access | Add `/var/run/docker.sock:/var/run/docker.sock` to template **Volumes** |
| `Invalid mount: expected key=value ...` | Socket put in the **Mounts** field with `host:container` syntax | Put it in **Volumes** (`host:container`), or use Mounts syntax `type=bind,source=...,destination=...` |
| `Test Connection` → `NullPointerException` (CertificateUtils) | TLS credential missing a field | Not needed for socket setup — set URI to `unix:///var/run/docker.sock`, credentials `none` |
| Harbor `Core service is not available` | `redis` (or a dependency) container was down | `cd <harbor-dir> && docker compose up -d`; verify all containers healthy |
| Push fails: `project mlops-lab not found` | Harbor project missing | Create project `mlops-lab` in Harbor UI |
| Port conflict on 8081 | Jenkins and Mongo Express both on 8081 | Mongo Express is mapped to host **8083** in `docker-compose.dev.yml` |

Notes:
- `localhost:8082` is HTTP. Docker treats `localhost` registries as insecure by default, so no extra daemon config is needed for the push.
- Because the agent uses the **host** Docker socket, `docker compose up` runs on the host daemon — the app containers appear on your host, not inside a nested daemon.

---

## 10. Quick verification

```bash
docker ps                                   # jenkins + harbor-* running
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8081/login          # 200
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8082/api/v2.0/ping  # 200
```

After a successful pipeline run:
- Dev app → http://localhost:8501
- Prod app → http://localhost:8502
- Image in Harbor → Projects → `mlops-lab` → `streamlit-app:latest`
