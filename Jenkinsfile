pipeline {
  // 파라미터: 어떤 서비스를 빌드할지 입력받음
  parameters {
    string(
      name: 'SERVICE',
      defaultValue: 'main_portal',
      description: '빌드할 서비스 이름을 입력하세요 (예: main_portal, politics, society, entertainment)'
    )
  }

  // 에이전트: Kubernetes의 kaniko PodTemplate 사용
  agent {
    kubernetes {
        inheritFrom 'kaniko-agent'
        defaultContainer 'jnlp'
    }
  }

  stages {
    stage('Docker Build & Push') {
      steps {
        script {
          // 빌드할 폴더 경로 계산
          def folder = (params.SERVICE == 'main_portal') 
                        ? 'main_portal' 
                        : "category_server/${params.SERVICE}"

          // ECR repository 이름 지정
          def repo = (params.SERVICE == 'main_portal') 
                      ? 'main-portal' 
                      : 'category'

          // 이미지 태그 지정
          def tag = (params.SERVICE == 'main_portal') 
                     ? 'latest' 
                     : params.SERVICE

          // kaniko 컨테이너에서 Docker 이미지 빌드 및 ECR로 push
          dir(folder) {
            container('kaniko') {
              sh "echo REPO: ${repo}, TAG: ${tag}"
            }
          }
        }
      }
    }
  }
}
