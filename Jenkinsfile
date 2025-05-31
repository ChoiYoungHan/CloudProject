pipeline {
  agent {
    kubernetes {
      inheritFrom 'kaniko-agent'
      defaultContainer 'jnlp'
      yaml """
        apiVersion: v1
        kind: Pod
        spec:
          containers:
            - name: jnlp
              image: jenkins/inbound-agent:alpine
              args: ['\${computer.jnlpmac}', '\${computer.name}']
              resources:
                requests:
                  memory: "512Mi"
                  cpu: "200m"
            - name: kaniko
              image: gcr.io/kaniko-project/executor:latest
              tty: true
              volumeMounts:
              - name: docker-config
                mountPath: /kaniko/.docker
              resources:
                requests:
                  memory: "1Gi"
                  cpu: "500m"
          volumes:
            - name: docker-config
              secret:
                secretName: kaniko-docker-config
      """
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
    stage('Docker Build & Push') {
      steps {
        timeout(time: 30, unit: 'MINUTES') {
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
                // 디버깅: 작업 디렉토리와 파일 확인
                sh """
                  echo "📁 작업 디렉토리: \$(pwd)"
                  ls -al
                  echo "📂 /workspace 디렉토리 확인:"
                  ls -al /workspace
                  echo "📂 /workspace/${folder} 디렉토리 확인:"
                  ls -al /workspace/${folder} || echo "디렉토리 ${folder} 없음"
                  echo "📄 Dockerfile 확인:"
                  cat /workspace/${folder}/Dockerfile || echo "Dockerfile 없음"
                  echo "📄 /kaniko/.docker/config.json 확인:"
                  cat /kaniko/.docker/config.json || echo "config.json 없음"
                """
                sh """
                  /kaniko/executor \
                    --context=/workspace/${folder} \
                    --dockerfile=/workspace/${folder}/Dockerfile \
                    --destination=207567776727.dkr.ecr.us-west-2.amazonaws.com/${repo}:${tag} \
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