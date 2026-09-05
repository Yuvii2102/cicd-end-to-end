pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
            }
        }

        stage('Verify Repository') {
            steps {
                sh '''
                    echo "Repository contents:"
                    ls -la

                    echo ""
                    echo "Git commit:"
                    git log -1 --oneline
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    echo "Building Docker image..."
                    docker build -t todo-app:${BUILD_NUMBER} .
                '''
            }
        }

        stage('Run Django Tests') {
            steps {
                sh '''
                    echo "Running Django tests..."
                    docker run --rm todo-app:${BUILD_NUMBER} python manage.py test
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {
                    def scannerHome = tool 'SonarQubeScanner'

                    withSonarQubeEnv('SonarQube') {
                        sh "${scannerHome}/bin/sonar-scanner"
                    }
                }
            }
        }

    }

    post {
        success {
            echo '✅ CI Pipeline completed successfully!'
        }

        failure {
            echo '❌ CI Pipeline failed!'
        }

        always {
            sh '''
                echo "Cleaning temporary Docker image..."
                docker rmi todo-app:${BUILD_NUMBER} || true
            '''
        }
    }
}
