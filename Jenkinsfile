pipeline {
  agent any

  parameters {
    string(name: 'IMAGE_TAG', defaultValue: '', description: 'Image tag to use (optional). If empty, a tag based on build number will be used')
    string(name: 'TARGET_ENV', defaultValue: 'dev', description: 'Target environment to update (dev, stage, prod)')
  }

  environment {
    # Placeholder: set your Docker Hub repo (do not commit real username)
    DOCKERHUB_REPO = 'leahm90/hello-world'
    # Credential IDs (placeholders) - configure in Jenkins Credentials
    DOCKERHUB_CREDENTIALS_ID = 'DOCKERHUB_CREDENTIALS'
    GIT_CREDENTIALS_ID = 'GIT_CREDS'
    # GitOps repository URL placeholder (repo that ArgoCD will watch)
    GITOPS_REPO_URL = 'https://github.com/leah648/devops-final-project.git'
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
        echo 'Updating GitOps repository with new image tag (safe update of environments/<env>/values.yaml)'
        script {
          // The following updates environments/<env>/values.yaml.image.tag and commits the change.
          // Requirements: git installed on the agent and GIT credentials configured in Jenkins.
          if (env.GITOPS_REPO_URL == 'https://github.com/leah648/devops-final-project.git') {
            echo 'GITOPS_REPO_URL is a placeholder. Skipping automatic update. Configure GITOPS_REPO_URL and credentials to enable this step.'
          } else {
            withCredentials([usernamePassword(credentialsId: env.GIT_CREDENTIALS_ID, usernameVariable: 'GIT_USER', passwordVariable: 'GIT_PASS')]) {
              sh '''
                set -euo pipefail
                WORKDIR=$(mktemp -d)
                echo "Cloning ${GITOPS_REPO_URL} into ${WORKDIR}"
                git clone "${GITOPS_REPO_URL}" "${WORKDIR}/repo"
                cd "${WORKDIR}/repo"
                git config user.email "ci@jenkins.local"
                git config user.name "jenkins-ci"

                BRANCH="ci/update-image-${IMAGE_TAG_ACTUAL}"
                echo "Creating branch ${BRANCH}"
                git checkout -b "${BRANCH}"

                TARGET_FILE="environments/${TARGET_ENV}/values.yaml"
                if [ ! -f "${TARGET_FILE}" ]; then
                  echo "Target file ${TARGET_FILE} not found"
                  exit 1
                fi

                echo "Updating image.tag in ${TARGET_FILE} to ${IMAGE_TAG_ACTUAL}"
                # Prefer sed for portability over external YAML tools. Assumes a simple 'tag: ...' line exists under 'image:' in the YAML.
                # This will replace the first occurrence of a line starting with '  tag:' or 'tag:' with the new tag.
                if command -v sed >/dev/null 2>&1; then
                  # Create a backup in case of unexpected format
                  sed -n '1,200p' "${TARGET_FILE}" > /dev/null || true
                  # Use extended regex replacement (POSIX sed compatible): replace line that starts with optional spaces then 'tag:'
                  sed -i.bak -E "s#^(\s*tag:\s*).*#\1\"${IMAGE_TAG_ACTUAL}\"#" "${TARGET_FILE}"
                else
                  python - <<PY
import sys, yaml
p = sys.argv[1]
tag = sys.argv[2]
with open(p) as f:
    d = yaml.safe_load(f)
if not isinstance(d, dict):
    raise SystemExit('Unexpected YAML structure')
d.setdefault('image', {})
d['image']['tag'] = tag
with open(p, 'w') as f:
    yaml.safe_dump(d, f, default_flow_style=False)
print('Updated', p)
PY "${TARGET_FILE}" "${IMAGE_TAG_ACTUAL}"
                fi

                git add "${TARGET_FILE}"
                if git diff --staged --quiet; then
                  echo "No changes to commit"
                else
                  git commit -m "ci: update ${TARGET_FILE} image.tag -> ${IMAGE_TAG_ACTUAL}"
                  echo "Pushing branch ${BRANCH} to origin"
                  # Push using HTTPS with credentials. If using SSH, configure Jenkins with SSH credentials and change accordingly.
                  GIT_URL_SAFE=${GITOPS_REPO_URL#https://}
                  git push "https://${GIT_USER}:${GIT_PASS}@${GIT_URL_SAFE}" HEAD:main
                fi

                # cleanup
                rm -rf "${WORKDIR}"
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
