pipeline {
    agent any

    environment {
        IMAGE       = "ajith0b1m/aceest-fitness"
        APP_VERSION = "1.0.0"
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
    }

    post {
        always { archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true 
	sh 'docker logout || true'
	}
    }
}
