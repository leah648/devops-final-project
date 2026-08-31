Argo Rollouts Canary deployment for hello-world

This folder contains an Argo Rollouts Rollout resource and a Service to enable canary deployments.

Files:
- rollout.yaml  - Argo Rollouts Rollout resource (canary strategy)
- service.yaml  - Kubernetes Service used for traffic shifting

What the rollout does:
- Uses a Canary strategy with three progressive traffic percentages: 20%, 50%, 100%.
- Pauses for 30s between each step to allow health checks and observability.
- Routes traffic via the Service named "hello-world-service" (port 80) — see service.yaml.
- The Rollout supports rollbacks via the argo-rollouts kubectl plugin commands.

Placeholders you must replace before use:
- <DOCKERHUB_USER>/hello-world:<TAG> in rollout/rollout.yaml — set to your image repository and tag.

Prerequisites:
- Argo Rollouts controller must be installed in your cluster: https://argoproj.github.io/argo-rollouts/installation/
- kubectl argo-rollouts plugin should be available locally to run rollout commands (https://argoproj.github.io/argo-rollouts/)

Basic usage examples

1) Apply the Service and Rollout:
   kubectl apply -f rollout/service.yaml
   kubectl apply -f rollout/rollout.yaml

2) Start a new rollout by updating the image (replace with your image):
   kubectl set image rollout/hello-world-rollout hello-world=<DOCKERHUB_USER>/hello-world:<NEW_TAG>

3) Observe rollout status (watching progress):
   kubectl argo-rollouts get rollout hello-world-rollout -w

4) Promote the rollout to stable (finish rollout immediately):
   kubectl argo-rollouts promote hello-world-rollout

5) Abort/rollback the rollout (stop and revert to stable):
   kubectl argo-rollouts abort hello-world-rollout

6) To inspect detailed history and see previous revisions:
   kubectl argo-rollouts history rollout hello-world-rollout

Notes on rollback

- If the rollout fails or health checks fail during canary steps, use the abort command to stop and rollback to the previous stable revision.
- You can also set the image back to a known-good tag using kubectl set image to trigger a new rollout for the stable version.

Validation

- After applying the manifests, use the argo-rollouts plugin to watch the rollout and verify traffic shifts.
- Confirm service endpoints and that /health returns status 200 for pods.

