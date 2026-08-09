pipeline {
    /*
     * Production Enterprise Pattern (DevOps Journey):
     * Uses a dynamic, ephemeral Docker Cloud Agent connected over TCP (JNLP).
     * Label 'docker-python-agent' triggers Jenkins to dynamically launch an agent container.
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
                echo 'Executing Python tests inside dynamic Jenkins TCP Docker Agent...'
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
