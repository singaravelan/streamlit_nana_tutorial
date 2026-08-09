pipeline {
    agent any

    stages {
        stage('Checkout Code') {
            steps {
                echo 'Checking out code from Git...'
                checkout scm
            }
        }

        stage('Smoke & Regression Tests') {
            steps {
                echo 'Running Python tests in an isolated ephemeral Python container...'
                // Using docker run to execute tests inside official python:3.11-slim container
                // This eliminates the need to install Python directly inside the Jenkins controller!
                sh 'docker run --rm -v $(pwd):/app -w /app python:3.11-slim sh -c "pip install -r requirements.txt && python tests/test_app.py"'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building updated application Docker image...'
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
