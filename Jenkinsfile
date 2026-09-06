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

                    docker tag todo-app:${BUILD_NUMBER} yuvi2102/todo-app:${BUILD_NUMBER}
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

                        docker push yuvi2102/todo-app:${BUILD_NUMBER}

                        echo "Docker image pushed successfully!"
                    '''
                }
            }
        }

        stage('Update Kubernetes Manifest') {
            steps {
                withCredentials([sshUserPrivateKey(
                    credentialsId: 'github-ssh',
                    keyFileVariable: 'SSH_KEY',
                    usernameVariable: 'GIT_USERNAME'
                )]) {
                    sh '''
                        echo "Updating Kubernetes image tag..."

                        sed -i "s|image: yuvi2102/todo-app:.*|image: yuvi2102/todo-app:${BUILD_NUMBER}|" deploy/deploy.yaml

                        echo ""
                        echo "Updated Kubernetes image:"
                        grep "image:" deploy/deploy.yaml

                        echo ""
                        echo "Configuring Git..."

                        git config user.name "Jenkins"
                        git config user.email "jenkins@localhost"

                        echo ""
                        echo "Committing Kubernetes manifest..."

                        git add deploy/deploy.yaml

                        git commit -m "Update Kubernetes image to ${BUILD_NUMBER}" || true

                        echo ""
                        echo "Pushing updated manifest to GitHub..."

                        GIT_SSH_COMMAND="ssh -i $SSH_KEY -o StrictHostKeyChecking=no" git push origin main

                        echo ""
                        echo "Kubernetes manifest pushed successfully!"
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

                docker rmi yuvi2102/todo-app:${BUILD_NUMBER} || true
            '''
        }
    }
}
