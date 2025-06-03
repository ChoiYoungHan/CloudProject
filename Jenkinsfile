pipeline {
    agent {
        kubernetes {
            yaml '''
apiVersion: v1
kind: Pod
metadata:
  labels:
    app: jenkins-agent
spec:
  serviceAccountName: kaniko
  containers:
  - name: kaniko
    image: gcr.io/kaniko-project/executor:v1.24.0-debug
    command:
    - sleep
    - "9999"
    tty: true
    volumeMounts:
    - name: aws-credentials
      mountPath: /root/.aws
      readOnly: true
  volumes:
  - name: aws-credentials
    secret:
      secretName: aws-credentials
'''
        }
    }
    environment {
        AWS_REGION = 'us-west-2'
        ECR_REGISTRY = '207567776727.dkr.ecr.us-west-2.amazonaws.com'
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Build and Push Images') {
            parallel {
                stage('Build Entertainment') {
                    steps {
                        container('kaniko') {
                            sh '''
                            /kaniko/executor \
                              --context `pwd`/category_server/entertainment \
                              --dockerfile `pwd`/category_server/entertainment/Dockerfile \
                              --destination ${ECR_REGISTRY}/category/entertainment:1.0.${BUILD_NUMBER} \
                              --cache=true \
                              --cache-dir=/cache \
                              --verbosity=debug
                            '''
                        }
                    }
                }
                stage('Build Politics') {
                    steps {
                        container('kaniko') {
                            sh '''
                            /kaniko/executor \
                              --context `pwd`/category_server/politics \
                              --dockerfile `pwd`/category_server/politics/Dockerfile \
                              --destination ${ECR_REGISTRY}/category/politics:1.0.${BUILD_NUMBER} \
                              --cache=true \
                              --cache-dir=/cache \
                              --verbosity=debug
                            '''
                        }
                    }
                }
                stage('Build Society') {
                    steps {
                        container('kaniko') {
                            sh '''
                            /kaniko/executor \
                              --context `pwd`/category_server/society \
                              --dockerfile `pwd`/category_server/society/Dockerfile \
                              --destination ${ECR_REGISTRY}/category/society:1.0.${BUILD_NUMBER} \
                              --cache=true \
                              --cache-dir=/cache \
                              --verbosity=debug
                            '''
                        }
                    }
                }
                stage('Build Main Portal') {
                    steps {
                        container('kaniko') {
                            sh '''
                            /kaniko/executor \
                              --context `pwd`/main_portal \
                              --dockerfile `pwd`/main_portal/Dockerfile \
                              --destination ${ECR_REGISTRY}/main-portal:1.0.${BUILD_NUMBER} \
                              --cache=true \
                              --cache-dir=/cache \
                              --verbosity=debug
                            '''
                        }
                    }
                }
            }
        }
    }
}