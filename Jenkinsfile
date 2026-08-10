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

    environment {
        DOCKER_HOST = 'tcp://dind:2375'
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

        stage('Build Docker Image') {
            steps {
                echo 'Building updated application Docker image...'
                sh 'docker compose -p streamlit_nana_tutorial -f docker-compose.dev.yml build'
            }
        }

        stage('Push Image to Harbor Registry') {
            steps {
                echo 'Logging into Harbor & Pushing image to localhost:8082/mlops-lab/streamlit-app:latest...'
                sh 'docker login localhost:8082 -u admin -p Harbor12345'
                sh 'docker tag streamlit_nana_tutorial-streamlit-app:latest localhost:8082/mlops-lab/streamlit-app:latest'
                sh 'docker push localhost:8082/mlops-lab/streamlit-app:latest'
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
