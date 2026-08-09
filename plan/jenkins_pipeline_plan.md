# Industry Best Practice: Jenkins CI/CD Pipeline with Dedicated Python Docker Agent

## Architecture Overview

```
[Developer] ➔ git push ➔ [GitHub Remote Repo]
                               │
                               ▼ (Poll SCM every 2 mins)
                       [Jenkins Controller]
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
[Jenkins Docker Agent: python:3.11-slim]   [Serving Container: streamlit-dev]
 - Installs requirements.txt                - Runs application 24/7
 - Runs Python tests/linters                - Untouched if tests fail
 - Builds updated Docker image              - Replaced only when build succeeds
 - Triggered via /var/run/docker.sock
```

---

## Why Use a Dedicated Jenkins Docker Agent?

1. **Clean Slate Execution**: Every build runs inside a brand new `python:3.11-slim` container isolated from your host system.
2. **Serving App Protection**: Tests NEVER execute inside `streamlit-dev`. If a test fails, `streamlit-dev` remains online and completely unaffected.
3. **No Controller Pollution**: No need to install Python, `pip`, or testing dependencies inside the Jenkins controller container.

---

## Updated `Jenkinsfile` Declarative Syntax

```groovy
pipeline {
    agent {
        docker {
            image 'python:3.11-slim'
            args '-v /var/run/docker.sock:/var/run/docker.sock -v /tmp:/tmp'
        }
    }

    stages {
        stage('Checkout Code') {
            steps {
                echo 'Checking out code from Git...'
                checkout scm
            }
        }

        stage('Smoke & Regression Tests') {
            steps {
                echo 'Executing Python tests inside isolated Python Docker Agent...'
                sh 'pip install --no-cache-dir -r requirements.txt'
                sh 'python tests/test_app.py'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building updated application Docker image via host Docker engine...'
                sh 'docker compose -f docker-compose.dev.yml build'
            }
        }

        stage('Deploy / Hot Reload') {
            steps {
                echo 'Deploying updated containers locally...'
                sh 'docker compose -f docker-compose.dev.yml up -d'
            }
        }
    }

    post {
        success {
            echo '🎉 CI/CD Pipeline succeeded! Application updated successfully.'
        }
        failure {
            echo '❌ CI/CD Pipeline failed! Check logs above.'
        }
    }
}
```

---

## Required Jenkins Plugin

For `agent { docker { ... } }` to work natively in Jenkins:
1. Go to **Manage Jenkins** ➔ **Plugins** ➔ **Available Plugins**.
2. Search and install **Docker Pipeline** (and **Docker** plugin).
3. Restart Jenkins if prompted.
