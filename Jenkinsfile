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

                    echo "Tagging image for Docker Hub..."
                    docker tag todo-app:${BUILD_NUMBER} yuvii2102/todo-app:${BUILD_NUMBER}
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

        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USERNAME',
                    passwordVariable: 'DOCKER_PASSWORD'
                )]) {
                    sh '''
                        echo "Logging in to Docker Hub..."

                        echo "$DOCKER_PASSWORD" | docker login \
                            -u "$DOCKER_USERNAME" \
                            --password-stdin

                        echo "Pushing Docker image..."

                        docker push yuvii2102/todo-app:${BUILD_NUMBER}

                        echo "Docker image pushed successfully!"
                    '''
                }
            }
        }
    }

    post {
        success {
            echo '✅ CI/CD Pipeline completed successfully!'
        }

        failure {
            echo '❌ CI/CD Pipeline failed!'
        }

        always {
            sh '''
                echo "Cleaning temporary Docker images..."

                docker rmi todo-app:${BUILD_NUMBER} || true
                docker rmi yuvii2102/todo-app:${BUILD_NUMBER} || true
            '''
        }
    }
}
