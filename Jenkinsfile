pipeline {
    agent any

    environment {
        IMAGE       = "ajith0b1m/aceest-fitness"
        APP_VERSION = "1.1.0"
    }

    triggers {
        pollSCM('H/2 * * * *')      // check GitHub about every 2 minutes
    }

    stages {
        stage('Install') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -q -r requirements.txt
                '''
            }
        }
        stage('Lint') {
            steps { sh '. venv/bin/activate && python -m ruff check .' }
        }
        stage('Unit Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    mkdir -p reports
                    python -m pytest --junitxml=reports/junit.xml \
                        --cov=ACEest_Fitness --cov-report=xml:reports/coverage.xml
                '''
            }
            post { always { junit 'reports/junit.xml' } }
        }
        stage('SonarQube Analysis') {
            steps {
                script {
                    def scannerHome = tool 'sonar-scanner'
                    withSonarQubeEnv('sonarqube') {
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
        stage('Docker Build') {
            steps {
                sh 'docker build --build-arg APP_VERSION=$APP_VERSION -t $IMAGE:$APP_VERSION -t $IMAGE:build-$BUILD_NUMBER .'
            }
        }
        stage('Test in Container') {
            steps { sh 'docker run --rm $IMAGE:$APP_VERSION python -m pytest -v' }
        }
        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub',
                                 usernameVariable: 'DH_USER', passwordVariable: 'DH_TOKEN')]) {
                    sh '''
                        echo "$DH_TOKEN" | docker login -u "$DH_USER" --password-stdin
                        docker push $IMAGE:$APP_VERSION
                        docker tag $IMAGE:$APP_VERSION $IMAGE:latest
                        docker push $IMAGE:latest
                    '''
                }
            }
        }
        stage('Deploy to Kubernetes') {
            steps {
                withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
                    sh '''
                        kubectl apply -f k8s/rolling-update/service.yaml
                        kubectl set image deployment/aceest-fitness aceest-fitness=$IMAGE:$APP_VERSION
                        kubectl annotate deployment/aceest-fitness --overwrite \
                            kubernetes.io/change-cause="Jenkins build $BUILD_NUMBER: version $APP_VERSION"
                        kubectl rollout status deployment/aceest-fitness --timeout=120s \
                            || (kubectl rollout undo deployment/aceest-fitness && exit 1)
                    '''
                }
            }
        }
        stage('Smoke Test') {
            steps {
                sh '''
                    curl -fs http://192.168.49.2:30080/health
                    curl -fs http://192.168.49.2:30080/version | grep -q "$APP_VERSION"
                '''
            }
            post {
                failure {
                    withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
                        sh 'kubectl rollout undo deployment/aceest-fitness'
                    }
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
            sh 'docker logout || true'
        }
    }
}
