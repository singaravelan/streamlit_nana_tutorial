# Industry Best Practice: Jenkins CI/CD Pipeline with Docker Agent & SCM Polling

## Architectural Principles (MLOps Best Practices)

1. **Clean Jenkins Controller**: 
   - Never install application runtimes (like Python, PyTorch, Node.js) directly inside the Jenkins controller container.
   - Jenkins acts strictly as an **orchestrator**.
2. **Ephemeral Docker Agents / Containers**:
   - Tests and code execution run inside temporary, isolated Docker containers (e.g., `python:3.11-slim`).
3. **Automated Triggering**:
   - Jenkins polls the GitHub repository (`git@github.com:singaravelan/streamlit_nana_tutorial.git`) every 2-5 minutes for new commits.
4. **Zero-Downtime Local Update**:
   - When a commit passes tests, Jenkins rebuilds the Docker image and executes `docker compose up -d --build` to update the running application automatically.

---

## Architecture Flow

```
[Developer] ➔ git push ➔ [GitHub Repo]
                             │
                             ▼ (Poll SCM every 2 mins)
                     [Jenkins Controller]
                             │
                             ├─► 1. Run Python Unit/Smoke Tests (in python:3.11-slim container)
                             ├─► 2. Build Docker Image (streamlit-app:latest)
                             └─► 3. Deploy/Update via docker compose
```

---

## Step 1: Create `Jenkinsfile` in Project Root

Add a declarative `Jenkinsfile` to your repository defining the stages:
1. **Checkout & Test**: Spins up a clean `python:3.11-slim` container, installs `requirements.txt`, and runs smoke tests.
2. **Build**: Builds the Streamlit app Docker image.
3. **Deploy**: Re-runs `docker compose up -d --build` to update the live app.

---

## Step 2: Configure Jenkins Job

1. Open Jenkins (`http://localhost:8080`).
2. Click **New Item** ➔ Name: `streamlit-mops-pipeline` ➔ Select **Pipeline**.
3. Under **Build Triggers**:
   - Check **Poll SCM**.
   - Schedule: `H/2 * * * *` (polls GitHub every 2 minutes for changes).
4. Under **Pipeline**:
   - Definition: **Pipeline script from SCM**
   - SCM: **Git**
   - Repository URL: `git@github.com:singaravelan/streamlit_nana_tutorial.git` (or HTTPS URL `https://github.com/singaravelan/streamlit_nana_tutorial.git`)
   - Branch Specifier: `*/main`
   - Script Path: `Jenkinsfile`
5. Save the job.

---

## Step 3: Verify Automated CI/CD Workflow

1. Make a small code change in `src/app.py`.
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update app feature"
   git push origin main
   ```
3. Within 2 minutes, Jenkins will detect the commit, trigger the build, execute tests in a Python container, and automatically update the running app!
