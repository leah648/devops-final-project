Argo CD application manifests and App of Apps

This folder contains Argo CD Application manifests used for GitOps deployment.

Structure:

- app-of-apps.yaml       - Parent Argo CD Application (App of Apps)
- apps/dev.yaml          - Child Application for Dev environment
- apps/stage.yaml        - Child Application for Stage environment
- apps/prod.yaml         - Child Application for Prod environment

Placeholders to replace before applying:

- https://github.com/leah648/devops-final-project.git : URL of the Git repository (this repository) that Argo CD will watch.

Notes:

- Each child Application points to the Helm chart at 'helm/hello-world' and uses the corresponding environment values file under 'environments/<env>/values.yaml' via helm.valueFiles.
- The parent Application (app-of-apps) points to 'argocd/apps' so Argo CD will deploy the child Application manifests as resources.
- The manifests assume Argo CD is installed in the 'argocd' namespace and that the 'argocd' namespace exists or CreateNamespace=true is used.

How to use:

1. Replace <GITOPS_REPO_URL> with your repository URL in all files.
2. Commit and push to your GitOps repository (the same repo or a separate repo as desired).
3. In your Argo CD instance, create the parent application by applying app-of-apps.yaml (or by using the UI):
   kubectl apply -f argocd/app-of-apps.yaml -n argocd

4. Argo CD will then synchronize the child applications listed under argocd/apps/ and deploy the Helm chart per environment.

Limitations and manual checks:

- The Helm chart must be present at helm/hello-world in the same repository.
- The environments values files must exist at the specified paths.
- The Kubernetes cluster must have permissions and ability to provision Service types used (NodePort/LoadBalancer).

