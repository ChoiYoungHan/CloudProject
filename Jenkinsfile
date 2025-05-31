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
                  memory: "256Mi"
                  cpu: "100m"
            - name: kaniko
              image: gcr.io/kaniko-project/executor:latest
              tty: true
              volumeMounts:
              - name: docker-config
                mountPath: /kaniko/.docker
          volumes:
            - name: docker-config
              secret:
                secretName: kaniko-docker-config
      """
      defaultContainer 'jnlp'
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
              sh "echo 📁 현재 디렉토리: \$(pwd)"
              sh "echo 📄 Dockerfile 확인: && ls -al && cat Dockerfile"
              sh """
                /kaniko/executor \
                  --context=dir://. \
                  --dockerfile=Dockerfile \
                  --destination=207567776727.dkr.ecr.us-west-2.amazonaws.com/main-portal:latest \
                  --docker-config=/kaniko/.docker \
                  --verbosity=info
              """
            }
          }
        }
      }
    }
  }
}
