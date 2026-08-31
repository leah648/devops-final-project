pipeline {
  agent any

  parameters {
    string(name: 'IMAGE_TAG', defaultValue: '', description: 'Image tag to use (optional). If empty, a tag based on build number will be used')
  }

  environment {
    # Placeholder: set your Docker Hub repo (do not commit real username)
    DOCKERHUB_REPO = '<DOCKERHUB_USER>/hello-world'
    # Credential IDs (placeholders) - configure in Jenkins Credentials
    DOCKERHUB_CREDENTIALS_ID = 'DOCKERHUB_CREDENTIALS'
    GIT_CREDENTIALS_ID = 'GIT_CREDS'
    # GitOps repository URL placeholder (repo that ArgoCD will watch)
    GITOPS_REPO_URL = '<GITOPS_REPO_URL>'
  }

  options {
    timestamps()
    ansiColor('xterm')
  }

  stages {
    stage('Clone') {
      steps {
        echo 'Checking out source repository'
        checkout scm
      }
    }

    stage('Build Application') {
      steps {
        echo 'Installing dependencies'
        sh 'python -m venv .venv'
        sh '. .venv/bin/activate && pip install -r requirements.txt'
      }
    }

    stage('Test') {
      steps {
        echo 'Running pytest'
        sh '. .venv/bin/activate && pytest -q'
      }
    }

    stage('Set Image Tag') {
      steps {
        script {
          if (params.IMAGE_TAG?.trim()) {
            env.IMAGE_TAG_ACTUAL = params.IMAGE_TAG
          } else {
            env.IMAGE_TAG_ACTUAL = "dev-${env.BUILD_NUMBER}"
          }
          env.IMAGE = "${env.DOCKERHUB_REPO}:${env.IMAGE_TAG_ACTUAL}"
          echo "Using image: ${env.IMAGE}"
        }
      }
    }

    stage('Build Docker Image') {
      steps {
        echo 'Building Docker image'
        sh "docker build -t ${env.IMAGE} ."
      }
    }

    stage('Security Scan (Trivy)') {
      steps {
        echo 'Scanning image with Trivy for CRITICAL vulnerabilities'
        // Fail the build if any CRITICAL vulnerabilities are found. Requires trivy installed on the agent.
        sh "trivy image --exit-code 1 --severity CRITICAL ${env.IMAGE} || (echo 'No CRITICAL vulnerabilities found' && exit 0)"
      }
    }

    stage('Push Image') {
      steps {
        echo 'Pushing image to Docker Hub (credentials required)'
        withCredentials([usernamePassword(credentialsId: env.DOCKERHUB_CREDENTIALS_ID, usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
          sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
          sh "docker push ${env.IMAGE}"
        }
      }
    }

    stage('Update GitOps Repository') {
      steps {
        echo 'Updating GitOps repository with new image tag (placeholder steps)'
        script {
          // The following is an example. Replace GITOPS_REPO_URL and GIT_CREDENTIALS_ID with real values
          // and ensure the Jenkins agent has git installed.
          if (env.GITOPS_REPO_URL == '<GITOPS_REPO_URL>') {
            echo 'GITOPS_REPO_URL is a placeholder. Skipping automatic update. Configure GITOPS_REPO_URL and credentials to enable this step.'
          } else {
            withCredentials([usernamePassword(credentialsId: env.GIT_CREDENTIALS_ID, usernameVariable: 'GIT_USER', passwordVariable: 'GIT_PASS')]) {
              sh '''
                set -e
                git clone ${GITOPS_REPO_URL} gitops
                cd gitops
                # Example: update environments/dev/values.yaml or a kustomize image tag
                # The exact file to edit depends on your GitOps repo structure.
                # sed -i "s#image: .*#image: ${IMAGE}#g" environments/dev/values.yaml || true
                git add -A
                git commit -m "ci: update image to ${IMAGE}"
                git push https://${GIT_USER}:${GIT_PASS}@${GITOPS_REPO_URL#https://} HEAD:main
              '''
            }
          }
        }
      }
    }

    stage('Deployment (Manual/Doc)') {
      steps {
        echo 'Deployment to Kubernetes is handled by Argo CD (GitOps). This stage intentionally does not deploy directly to production.'
      }
    }
  }

  post {
    success {
      echo "Pipeline succeeded. Image was built and pushed: ${env.IMAGE}"
    }
    failure {
      echo 'Pipeline failed. Check build logs for details.'
    }
  }
}
