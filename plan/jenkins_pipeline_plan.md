# Production Enterprise Pattern: Jenkins TCP Docker Cloud Agents (DevOps Journey Architecture)

## Architecture Overview

```
                                    [GitHub Remote Repo]
                                             │
                                             ▼ (Poll SCM every 2 mins)
                                     [Jenkins Controller]
                                    (Ports: 8080 UI, 50000 TCP)
                                             │
                    (Triggers via Docker API over unix/TCP socket)
                                             │
                                             ▼
                 ┌──────────────────────────────────────────────────────┐
                 │ Ephemeral Docker Cloud Agent (docker-python-agent)   │
                 │  - Image: jenkins/inbound-agent:alpine (or python)   │
                 │  - Connects back to Controller via TCP port 50000    │
                 │  - Joined to 'mlops-network'                         │
                 │  - Executes tests, builds app, then DELETES ITSELF   │
                 └──────────────────────────────────────────────────────┘
                                             │
                                             ▼
                             [Serving App: streamlit-dev]
```

---

## Step-by-Step Setup Guide (DevOps Journey Method)

### Step 1: Ensure Shared Docker Network Exists
Create a shared Docker network if it doesn't already exist:
```bash
docker network create mlops-network
```

### Step 2: Spin Up Jenkins Controller with Port 50000 Exposed
Use `docker-compose.jenkins.yml`:
```bash
docker compose -f docker-compose.jenkins.yml up -d
```
*(Notice port `50000:50000` is exposed for TCP Inbound Agents).*

---

### Step 3: Install Docker Cloud Plugin in Jenkins
1. Open Jenkins at `http://localhost:8080`.
2. Go to **Manage Jenkins** ➔ **Plugins** ➔ **Available Plugins**.
3. Search for **Docker** (by *Docker Cloud Plugin / CloudBees*).
4. Select it and click **Install without restart**.

---

### Step 4: Configure Jenkins TCP Agent Port
1. Go to **Manage Jenkins** ➔ **Security**.
2. Under **Agents**:
   - Change from *Disabled* to **Fixed: 50000** (or **Random**).
3. Click **Save**.

---

### Step 5: Configure the Docker Cloud & Agent Template
1. Go to **Manage Jenkins** ➔ **Clouds** (or **Nodes and Clouds** ➔ **Clouds**).
2. Click **Add a new cloud** ➔ Select **Docker**.
3. Configure **Docker Cloud Details**:
   - **Docker Cloud Name**: `docker-local`
   - **Docker Host URI**: `unix:///var/run/docker.sock`
   - Click **Test Connection** (verify it shows success/version).
4. Configure **Docker Agent Template**:
   - Click **Add Docker Template**.
   - **Labels**: `docker-python-agent`
   - **Enabled**: Checked
   - **Name**: `python-build-agent`
   - **Docker Image**: `jenkins/inbound-agent:alpine` (or your custom Python agent)
   - **Instance Capacity**: `2`
   - **Remote Filing Directory**: `/home/jenkins/agent`
   - **Network**: `mlops-network`
5. Click **Save**.

---

### Step 6: Trigger & Test
When a git commit is pushed to `main`:
1. Jenkins Controller detects the commit via Poll SCM.
2. Jenkins uses the Docker Cloud plugin to launch an agent container labeled `docker-python-agent` on `mlops-network`.
3. The agent connects to Jenkins Controller over TCP port 50000.
4. The agent runs your build/test stages and automatically terminates!
