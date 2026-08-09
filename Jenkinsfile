pipeline {
    /*
     * Enterprise TCP Docker Cloud Agent Architecture (DevOps Journey Pattern):
     * Runs on jenkins/inbound-agent:alpine connected over TCP (port 50000).
     */
    agent {
        label 'docker-python-agent'
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
                sh 'python3 -m venv venv'
                sh '. venv/bin/activate && pip install --no-cache-dir -r requirements.txt && python tests/test_app.py'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building updated application Docker image via host Docker engine...'
                sh 'docker compose -p streamlit_nana_tutorial -f docker-compose.dev.yml build'
            }
        }

        stage('Deploy / Hot Reload') {
            steps {
                echo 'Deploying updated containers locally...'
                sh 'docker compose -p streamlit_nana_tutorial -f docker-compose.dev.yml up -d'
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
