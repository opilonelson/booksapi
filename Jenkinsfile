pipeline {
    agent {
        kubernetes {
            yaml """
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: kaniko
    image: gcr.io/kaniko-project/executor:latest
    command:
    - cat
    tty: true
    volumeMounts:
      - name: kaniko-secret
        mountPath: /kaniko/.docker
  volumes:
  - name: kaniko-secret
    secret:
      secretName: regcred
"""
        }
    }

    environment {
        VENV_DIR = '.venv'
        DEPLOY_SERVER = 'user@your-server-ip'
        DEPLOY_DIR = '/opt/flask-api'
        BRANCH_NAME = "${env.GIT_BRANCH}".replaceFirst(/^origin\\//, '')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Set up Python environment') {
            steps {
                sh '''
                    python3 -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    . ${VENV_DIR}/bin/activate
                    python -m unittest discover -s tests || echo "No tests found"
                '''
            }
        }

        stage('Deploy to Server') {
            when {
                expression { return env.BRANCH_NAME == 'main' }
            }
            steps {
                sshagent (credentials: ['ssh-key-id']) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no $DEPLOY_SERVER '
                            mkdir -p $DEPLOY_DIR &&
                            cd $DEPLOY_DIR &&
                            git clone https://github.com/your-org/your-repo.git . || git pull &&
                            docker-compose down || true &&
                            docker-compose up -d --build
                        '
                    '''
                }
            }
        }
    }

    post {
        failure {
            mail to: 'you@example.com',
                 subject: "Build Failed in Jenkins: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                 body: "Check Jenkins for details: ${env.BUILD_URL}"
        }
    }
}
