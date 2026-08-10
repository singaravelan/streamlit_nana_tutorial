pipeline {
    /*
     * Enterprise MLOps Pipeline with Harbor Registry & Dual Deployments:
     * - Runs on dynamic TCP Docker Cloud Agent (jenkins/inbound-agent:alpine)
     * - Runs Python Smoke & Regression tests in /tmp/venv
     * - Builds & tags Docker image for Harbor
     * - Pushes image to Harbor Private Registry (localhost:8082)
     * - Deploys Development App (Port 8501) & Production App (Port 8502)
     */
    agent {
        label 'docker-python-agent'
    }

    options {
        disableConcurrentBuilds()
        timeout(time: 45, unit: 'MINUTES')
    }

    environment {
        REGISTRY_HOST = 'localhost:8082'
        IMAGE_NAME = 'mlops-lab/streamlit-app:latest'
    }

    stages {
        stage('Checkout Code') {
            steps {
                echo 'Checking out code from Git...'
                checkout scm
            }
        }

        stage('Install Agent Tools') {
            steps {
                echo 'Installing Python3, Pip, Docker CLI, and Docker Compose inside Alpine Agent...'
                sh 'apk add --no-cache python3 py3-pip docker-cli docker-compose'
            }
        }

        stage('Smoke & Regression Tests') {
            steps {
                echo 'Executing Python smoke and regression tests...'
                // Using /tmp/venv outside workspace folder to keep workspace clean for Git Poll SCM
                sh 'python3 -m venv /tmp/venv'
                sh '. /tmp/venv/bin/activate && pip install --no-cache-dir -r requirements.txt && python tests/test_app.py'
            }
        }

        stage('Validate Docker Daemon Security') {
            steps {
                echo 'Validating secure Docker daemon configuration (TLS required)...'
                sh '''#!/bin/sh
set -eu
[ -n "${DOCKER_HOST:-}" ] || { echo "DOCKER_HOST is required"; exit 1; }
[ "${DOCKER_TLS_VERIFY:-}" = "1" ] || { echo "DOCKER_TLS_VERIFY must be 1"; exit 1; }
[ -n "${DOCKER_CERT_PATH:-}" ] || { echo "DOCKER_CERT_PATH is required"; exit 1; }
[ -f "${DOCKER_CERT_PATH}/ca.pem" ] || { echo "Missing ${DOCKER_CERT_PATH}/ca.pem"; exit 1; }
[ -f "${DOCKER_CERT_PATH}/cert.pem" ] || { echo "Missing ${DOCKER_CERT_PATH}/cert.pem"; exit 1; }
[ -f "${DOCKER_CERT_PATH}/key.pem" ] || { echo "Missing ${DOCKER_CERT_PATH}/key.pem"; exit 1; }
echo "$DOCKER_HOST" | grep -q ':2376' || { echo "DOCKER_HOST must use TLS port 2376"; exit 1; }
docker version >/dev/null
'''
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building updated application Docker image...'
                sh 'docker compose -p streamlit_nana_tutorial -f docker-compose.dev.yml build'
            }
        }

        stage('Push Image to Harbor Registry') {
            steps {
                echo 'Logging into Harbor and pushing image...'
                withCredentials([usernamePassword(credentialsId: 'harbor-admin', usernameVariable: 'HARBOR_USER', passwordVariable: 'HARBOR_PASS')]) {
                    sh '''#!/bin/sh
set -eu
echo "$HARBOR_PASS" | docker login "$REGISTRY_HOST" -u "$HARBOR_USER" --password-stdin
docker tag streamlit_nana_tutorial-streamlit-app:latest "$REGISTRY_HOST/$IMAGE_NAME"
docker push "$REGISTRY_HOST/$IMAGE_NAME"
docker logout "$REGISTRY_HOST"
'''
                }
            }
        }

        stage('Deploy Development App') {
            steps {
                echo 'Hot-reloading local Development Environment (Port 8501)...'
                sh 'docker compose -p streamlit_nana_tutorial -f docker-compose.dev.yml up -d'
            }
        }

        stage('Deploy Production App') {
            steps {
                echo 'Deploying Production App from Harbor Registry (Port 8502)...'
                sh 'docker compose -p streamlit_prod -f production_env/docker-compose.prod.yml up -d'
            }
        }
    }

    post {
        success {
            echo '🎉 CI/CD Pipeline succeeded! Image pushed to Harbor and Production deployed.'
        }
        failure {
            echo '❌ CI/CD Pipeline failed! Check logs above.'
        }
    }
}
