pipeline {
    /*
     * Production Enterprise Pattern (DevOps Journey):
     * Runs on dynamic TCP Docker Cloud Agent (jenkins/inbound-agent:alpine).
     * Uses ephemeral python:3.11-slim container for testing & host docker engine for build/deploy.
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

        stage('Smoke & Regression Tests') {
            steps {
                echo 'Executing Python tests inside isolated ephemeral python:3.11-slim container...'
                sh 'docker run --rm -v $(pwd):/app -w /app python:3.11-slim sh -c "pip install --no-cache-dir -r requirements.txt && python tests/test_app.py"'
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
