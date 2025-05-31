pipeline {
  agent {
    kubernetes {
      inheritFrom 'kaniko-agent'
      podRetention always()  
      defaultContainer 'jnlp'
      yaml '''
        apiVersion: v1
        kind: Pod
        metadata:
          labels:
            app: jenkins-pipeline
        spec:
          containers:
            - name: jnlp
              image: jenkins/inbound-agent:alpine
              args: ['${computer.jnlpmac}', '${computer.name}']
              resources:
                requests:
                  memory: "512Mi"
                  cpu: "200m"
            - name: kaniko
              image: gcr.io/kaniko-project/executor:debug  
              tty: true
              volumeMounts:
              - name: docker-config
                mountPath: /kaniko/.docker
              resources:
                requests:
                  memory: "1Gi"
                  cpu: "500m"
                limits:
                  memory: "2Gi"
                  cpu: "1"
          volumes:
            - name: docker-config
              secret:
                secretName: kaniko-docker-config
      '''
    }
  }

  parameters {
    string(
      name: 'SERVICE',
      defaultValue: 'main_portal',
      description: '빌드할 서비스 이름을 입력하세요 (예: main_portal, politics, society, entertainment)'
    )
  }

  stages {
    stage('Checkout SCM') {
      steps {
        checkout scm
        sh '''
          echo "📁 작업 디렉토리 확인:"
          pwd
          ls -al
          echo "📂 /workspace 디렉토리 확인:"
          ls -al /workspace
          echo "📂 /workspace/main_portal 디렉토리 확인:"
          ls -al /workspace/main_portal || echo "main_portal 디렉토리 없음"
          echo "📂 /workspace/category_server 디렉토리 확인:"
          ls -al /workspace/category_server || echo "category_server 디렉토리 없음"
        '''
      }
    }
    stage('Docker Build & Push') {
      steps {
        timeout(time: 60, unit: 'MINUTES') {
          script {
            def folder = (params.SERVICE == 'main_portal') 
                          ? 'main_portal' 
                          : "category_server/${params.SERVICE}"
            def dockerfile = "${folder}/Dockerfile"
            def repo = (params.SERVICE == 'main_portal') 
                        ? 'main-portal' 
                        : 'category'
            def tag = (params.SERVICE == 'main_portal') 
                       ? 'latest' 
                       : params.SERVICE

            dir(folder) {
              container('kaniko') {
                sh '''
                  echo "📁 Kaniko 작업 디렉토리: $(pwd)"
                  echo "📂 /workspace 디렉토리 확인:"
                  ls -al /workspace
                  echo "📂 /workspace/'${folder}' 디렉토리 확인:"
                  ls -al /workspace/'${folder}' || echo "디렉토리 '${folder}' 없음"
                  echo "📄 Dockerfile 확인:"
                  cat /workspace/'${folder}'/Dockerfile || echo "Dockerfile 없음"
                  echo "📄 /kaniko/.docker/config.json 확인:"
                  cat /kaniko/.docker/config.json || echo "config.json 없음"
                  echo "📄 Kaniko 실행기 확인:"
                  ls -al /kaniko/executor || echo "executor 없음"
                  echo "📄 셸 확인:"
                  ls -al /bin/sh /busybox/sh || echo "셸 없음"
                '''
                sh """
                  /kaniko/executor \
                    --context=/workspace/main-portal \
                    --dockerfile=/workspace/main-portal/Dockerfile \
                    --destination=207567776727.dkr.ecr.us-west-2.amazonaws.com/main-portal:latest \
                    --docker-config=/kaniko/.docker \
                    --verbosity=debug
                """
              }
            }
          }
        }
      }
    }
  }
}