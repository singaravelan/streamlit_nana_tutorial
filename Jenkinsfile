pipeline {
    /*
     * Jenkins Docker Agent Configuration:
     * Uses official python:3.11-slim container as the dedicated build/test agent.
     * Mounts docker socket so agent can trigger docker build & docker compose deploy.
     */
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
