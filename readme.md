# DevOps Final Project – CI/CD & GitOps Pipeline

## 1. Project Objective

Build a complete DevOps CI/CD and GitOps pipeline that automatically:

1. Builds a web application
2. Builds a Docker image
3. Scans the image for security vulnerabilities
4. Pushes the image to Docker Hub
5. Packages the application using Helm
6. Updates GitOps deployment configuration
7. Deploys the application to Kubernetes using Argo CD
8. Performs Canary deployments using Argo Rollouts
9. Supports multiple environments: Dev, Stage, and Prod
10. Automatically manages all environments using an Argo CD App of Apps

The final architecture should follow:

```text
GitHub
   |
   v
Jenkins CI
   |
   +--> Build Application
   |
   +--> Build Docker Image
   |
   +--> Trivy Security Scan
   |
   +--> Push Image to Docker Hub
   |
   +--> Helm Package / GitOps Update
   |
   v
Git Repository (GitOps)
   |
   v
Argo CD
   |
   v
Kubernetes Cluster
   |
   v
Argo Rollouts
   |
   v
Canary Deployment
```

---

# 2. Application

Create a simple web application.

Use Flask unless there is a strong technical reason to use another framework.

The application must display:

```text
Hello World
```

Create a health endpoint:

```text
/health
```

The health endpoint should return HTTP 200.

Example response:

```json
{
  "status": "healthy"
}
```

The application should listen on port `5000`.

Add automated tests using `pytest`.

---

# 3. Source Control

All project source code must be stored in GitHub.

The repository must contain at least:

```text
.
├── app/
├── Dockerfile
├── Jenkinsfile
├── k8s/
│   ├── deployment.yaml
│   └── service.yaml
├── helm/
│   └── hello-world/
├── environments/
│   ├── dev/
│   ├── stage/
│   └── prod/
├── argocd/
├── rollout/
├── README.md
└── .gitignore
```

The structure may be improved if necessary, but all mandatory requirements must remain clearly identifiable.

---

# 4. Docker

Create a Dockerfile for the application.

The image must be buildable using:

```bash
docker build -t <dockerhub-user>/hello-world:v1 .
```

The image must be pushable using:

```bash
docker push <dockerhub-user>/hello-world:v1
```

The Dockerfile should:

* Use an appropriate Python base image
* Install application dependencies
* Copy the application
* Expose port 5000
* Start the application
* Avoid running as root where practical
* Follow reasonable Docker best practices

Do not hard-code passwords or credentials.

---

# 5. Jenkins CI Pipeline

Create a `Jenkinsfile`.

The Jenkins pipeline must perform the following stages:

### Stage 1 – Clone

Clone the GitHub repository.

### Stage 2 – Build Application

Install dependencies and build/prepare the application.

### Stage 3 – Test

Run automated tests.

Example:

```bash
pytest
```

### Stage 4 – Build Docker Image

Build the Docker image.

Example:

```bash
docker build -t <dockerhub-user>/hello-world:v1 .
```

### Stage 5 – Security Scan

Run Trivy against the Docker image before pushing it.

Example:

```bash
trivy image <dockerhub-user>/hello-world:v1
```

The pipeline must fail if CRITICAL vulnerabilities are detected.

### Stage 6 – Push Image

Push the image to Docker Hub.

Example:

```bash
docker push <dockerhub-user>/hello-world:v1
```

Docker Hub credentials must be stored securely in Jenkins Credentials.

Never hard-code credentials in the Jenkinsfile.

### Stage 7 – Deployment

The final deployment mechanism should use GitOps with Argo CD.

Do not make Jenkins directly responsible for the normal production deployment when Argo CD is configured.

Jenkins is responsible primarily for CI and publishing the artifact/image and updating the GitOps source.

---

# 6. Kubernetes

Create:

```text
k8s/
├── deployment.yaml
└── service.yaml
```

## Deployment

Requirements:

* Minimum 2 replicas
* Container image must be configurable
* Resource requests must be defined
* Resource limits must be defined
* Appropriate labels/selectors
* Readiness probe
* Liveness probe
* Application listens on port 5000

Example resource configuration:

```yaml
resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    cpu: "500m"
    memory: "256Mi"
```

These values may be adjusted if appropriate.

## Service

Create a Kubernetes Service.

The service must use either:

* NodePort
* LoadBalancer

The application must be accessible from a browser.

---

# 7. Security – Trivy

Install/use Trivy.

The Docker image must be scanned before it is pushed to Docker Hub.

Example:

```bash
trivy image <dockerhub-user>/hello-world:v1
```

The Jenkins pipeline must fail when CRITICAL vulnerabilities are found.

Do not push an image before the security scan succeeds.

---

# 8. Helm

Convert the Kubernetes deployment into a Helm Chart.

Required structure:

```text
helm/
└── hello-world/
    ├── Chart.yaml
    ├── values.yaml
    └── templates/
        ├── deployment.yaml
        └── service.yaml
```

The Helm chart must allow configuration of at least:

* Replica count
* Image repository
* Image tag
* Container port
* Service type
* Service port
* Resource requests
* Resource limits

Do not hard-code environment-specific values inside the templates.

The chart must be installable with:

```bash
helm install hello-world ./helm/hello-world
```

Validate the chart using:

```bash
helm lint ./helm/hello-world
```

---

# 9. GitOps – Argo CD

Use Argo CD for Kubernetes deployment.

Create an Argo CD Application.

The application must:

* Point to the GitHub GitOps source
* Deploy the Helm chart
* Synchronize automatically
* Automatically correct drift where appropriate

Argo CD should be the normal deployment mechanism.

The desired flow is:

```text
Jenkins
   |
   | Build + Test + Scan + Push
   |
   v
Docker Hub

Jenkins / CI
   |
   | Update GitOps configuration
   v
GitHub
   |
   v
Argo CD
   |
   v
Kubernetes
```

---

# 10. Multi-Environment Deployment

Create three environments:

```text
environments/
├── dev/
├── stage/
└── prod/
```

Each environment must have different:

* Replica count
* Image tag
* Resource limits

For example:

```text
DEV
replicas: 1
image tag: dev
lower resources

STAGE
replicas: 2
image tag: stage
medium resources

PROD
replicas: 3
image tag: prod
higher resources
```

The exact values may be selected by the implementation.

The environment configuration must be stored in Git.

---

# 11. Argo CD App of Apps

Create a parent Argo CD Application.

The parent application must manage:

```text
Dev
Stage
Prod
```

The desired structure is:

```text
Argo CD
   |
   v
App of Apps
   |
   +--> Dev Application
   |
   +--> Stage Application
   |
   +--> Prod Application
```

All applications must be automatically deployed from Git.

---

# 12. Argo Rollouts – Canary Deployment

This project uses Argo Rollouts for Canary deployments. The Helm chart in this repository now renders an Argo Rollouts `Rollout` resource (instead of a plain `Deployment`) when `rollout.enabled` is true in the chart values. This enables gradual traffic shifting and safe rollbacks driven by GitOps.

Goals and requirements

- Gradually shift traffic from the stable version to the new (canary) version.
- Minimum three rollout steps (example: 20%, 50%, 100%).
- Support rollback and provide a documented rollback procedure.

Built-in chart behavior

- The Helm chart `helm/hello-world` produces a `Rollout` resource using the values at `environments/<env>/values.yaml`.
- Rollout steps and pause durations are configurable via `values.yaml` under the `rollout` key. Example default in `helm/hello-world/values.yaml`:

```yaml
rollout:
  enabled: true
  steps:
    - setWeight: 20
      pause:
        duration: 30s
    - setWeight: 50
      pause:
        duration: 30s
    - setWeight: 100
      pause:
        duration: 30s
```

Notes and prerequisites

- The Argo Rollouts controller (CRDs and controller) must be installed in the target cluster for `Rollout` resources to work: https://argoproj.github.io/argo-rollouts/installation/
- Argo CD supports CRDs and will manage `Rollout` resources as part of the chart.
- Replace placeholders such as `<DOCKERHUB_USER>` and `<TAG>` in your environment/CI pipeline before applying resources.

Helm commands (local validation)

- Lint the chart:

```bash
helm lint ./helm/hello-world
```

- Render templates (inspect the produced Rollout and Service YAML):

```bash
helm template hello-world ./helm/hello-world -f environments/dev/values.yaml
```

- Install the chart into a namespace (example for dev):

```bash
helm install hello-world-dev ./helm/hello-world -n hello-world-dev --create-namespace -f environments/dev/values.yaml
```

Argo Rollouts commands (runtime operations)

1) Start a new rollout (update the image on the Rollout):

```bash
kubectl set image rollout/<RELEASE-NAME>-hello-world <container-name>=<DOCKERHUB_USER>/hello-world:<NEW_TAG>
# Example if using fullname helper: kubectl set image rollout/hello-world-dev-hello-world hello-world=<DOCKERHUB_USER>/hello-world:dev-123
```

2) Observe rollout status (watch progress and health):

```bash
kubectl argo-rollouts get rollout <ROLLOUT_NAME> -w
# or use Argo CD UI to inspect the Rollout
```

3) Promote the rollout to stable (immediately finish and set canary as stable):

```bash
kubectl argo-rollouts promote <ROLLOUT_NAME>
```

4) Abort / Rollback the rollout (stop and revert to previous stable revision):

```bash
kubectl argo-rollouts abort <ROLLOUT_NAME>
# Alternatively, set the image back to a known-good tag to trigger a stable rollout:
kubectl set image rollout/<ROLLOUT_NAME> <container-name>=<DOCKERHUB_USER>/hello-world:<KNOWN_GOOD_TAG>
```

Example workflow (GitOps-driven)

1. CI pipeline builds and scans an image, then pushes it to the image registry and updates the environment values file under `environments/<env>/values.yaml` (image.tag).
2. Argo CD detects the change in Git and applies the Helm chart, producing a new `Rollout` revision.
3. Argo Rollouts performs the Canary steps according to the configured `rollout.steps`.
4. Operators can observe, promote, or abort the rollout using the `kubectl argo-rollouts` plugin or the Argo CD UI.

Rollback demonstration

- To demonstrate rollback, trigger a rollout to a new tag that fails health checks (or simulate a failure), then use:

```bash
kubectl argo-rollouts abort <ROLLOUT_NAME>
```

- Verify the Rollout returns to the previous stable revision and that service traffic is restored to the stable pods.

Manual validation checklist for Rollouts

- [ ] Argo Rollouts controller installed in cluster
- [ ] Helm chart renders a `Rollout` resource when `rollout.enabled: true`
- [ ] Argo CD applies the chart and creates `Rollout` resource
- [ ] Rollout proceeds through 20/50/100 (or configured) steps during an image update
- [ ] Promote and abort commands behave as expected

---

---

# 13. Horizontal Pod Autoscaler – Bonus

If implemented, add an HPA.

The HPA should scale the application based on CPU utilization.

Document:

* Minimum replicas
* Maximum replicas
* CPU target
* How to verify scaling

This feature is considered a bonus and must not break the mandatory requirements.

---

# 14. Required Prerequisites

Document installation/configuration requirements for:

* Git
* Docker
* Jenkins
* Kubernetes
* k3s or equivalent Kubernetes distribution
* Trivy
* Helm
* Argo CD
* Argo Rollouts

The project should preferably be testable using k3s.

---

# 15. README Documentation Requirements

This README must eventually contain:

## Project Overview

Explain what the project does.

## Architecture

Include an architecture diagram or Mermaid diagram showing:

```text
GitHub
   ↓
Jenkins CI
   ↓
Trivy
   ↓
Docker Hub
   ↓
GitOps Repository
   ↓
Argo CD
   ↓
Kubernetes
   ↓
Argo Rollouts
   ↓
Application
```

## Repository Structure

Explain the purpose of each important directory.

## Prerequisites

Explain what needs to be installed.

## Local Application

Explain how to run the application locally.

## Docker

Explain how to:

* Build the image
* Run the container
* Push the image

## Jenkins

Explain:

* Jenkins setup
* Required credentials
* Pipeline configuration
* How to run the pipeline

## Trivy

Explain how to run the security scan.

## Kubernetes

Explain how to deploy manually for testing.

## Helm

Explain:

```bash
helm lint ./helm/hello-world
helm install hello-world ./helm/hello-world
```

## Argo CD

Explain:

* Installation
* Application configuration
* Automatic synchronization

## Environments

Explain Dev, Stage and Prod.

## App of Apps

Explain the parent-child Argo CD structure.

## Canary Deployment

Explain:

* How Canary works
* The traffic percentages
* How to promote
* How to rollback

## Screenshots

Include a screenshot of a successful Jenkins pipeline.

Also include useful screenshots of:

* Jenkins pipeline
* Docker image
* Kubernetes pods
* Argo CD applications
* Successful rollout
* Canary deployment

## Troubleshooting

Include common problems and solutions.

Examples:

* Jenkins cannot access Docker
* Docker authentication failure
* Trivy scan failure
* Kubernetes pods not starting
* ImagePullBackOff
* Service not accessible
* Helm installation failure
* Argo CD synchronization failure
* Canary rollout failure

---

# 16. Security Requirements

Never commit:

* Passwords
* API keys
* Docker Hub passwords
* Jenkins secrets
* Kubernetes credentials
* Private tokens

Use:

* Jenkins Credentials
* Kubernetes Secrets where necessary
* Environment variables
* GitHub/Jenkins secret mechanisms

Add sensitive files to `.gitignore`.

---

# 17. AI Implementation Instructions

You are acting as a senior DevOps engineer.

Your task is to implement this project completely according to the requirements in this README.

Before making changes:

1. Inspect the repository.
2. Inspect all existing files.
3. Determine what already exists.
4. Do not unnecessarily overwrite working files.
5. Create missing directories/files.
6. Follow the requirements in this README exactly.

Implement the project in the following order:

```text
1. Flask application
2. Tests
3. Dockerfile
4. Kubernetes manifests
5. Helm chart
6. Jenkinsfile
7. Trivy integration
8. GitOps structure
9. Argo CD Application
10. Multi-environment configuration
11. Argo CD App of Apps
12. Argo Rollouts Canary deployment
13. HPA bonus
14. Documentation
15. Final validation
```

After every major stage:

* Run appropriate validation commands.
* Check for syntax errors.
* Check YAML validity.
* Run application tests.
* Run Docker build where possible.
* Run `helm lint`.
* Validate Kubernetes manifests where possible.
* Fix errors before continuing.

Do not simply create files and assume they work.

When something cannot be tested because it requires external infrastructure, clearly state what must be tested manually.

Do not invent:

* Docker Hub usernames
* Jenkins credentials
* GitHub repository URLs
* Kubernetes cluster addresses
* passwords
* tokens

Use placeholders where user-specific information is required.

At the end, create a final validation checklist mapping every requirement in this README to the implementation.

Use this format:

```text
[PASS] Application – Hello World
[PASS] GitHub repository
[PASS] Dockerfile
[PASS] Jenkins pipeline
[PASS] Docker Hub push
[PASS] Trivy scan
[PASS] Kubernetes Deployment
[PASS] Kubernetes Service
[PASS] Helm
[PASS] Argo CD
[PASS] Dev environment
[PASS] Stage environment
[PASS] Prod environment
[PASS] App of Apps
[PASS] Argo Rollouts
[PASS] Canary deployment
[PASS] Rollback
[PASS] HPA (Bonus)
[PASS] Documentation
```

Do not mark an item as PASS unless it has actually been implemented and validated.
