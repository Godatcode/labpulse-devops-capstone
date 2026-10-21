# LabPulse presentation walkthrough

This is the sequence used for the captioned screen recording. The slides introduce the system, followed by live browser and terminal checks. The AWS cluster is destroyed after the short recording window.

## 1. Slides (about 2 minutes)

Open `slides.pdf`. Explain why shared lab equipment needs a status and incident register. Walk through the browser, API, database, CI pipeline, Terraform, Kubernetes, and monitoring slides. On the AWS slide, say that the cluster was provisioned and then destroyed after the evidence was captured.

## 2. Code and local application (about 2 minutes)

Show `backend/app/`, `backend/alembic/versions/`, `frontend/`, `docker-compose.yml`, `.github/workflows/ci.yml`, `terraform/`, `helm/labpulse/`, and `monitoring/`. Run `docker compose up --build -d`, open `http://localhost:3000`, create or update an incident, and open `http://localhost:8000/docs`.

## 3. CI and security (about 2 minutes)

Open the latest successful GitHub Actions run. Point to the API tests, frontend build, Docker builds, Trivy scans, and GHCR publication with commit SHA tags. If the assessment requires a new push during the recording, make a small genuine code or documentation change first, then wait for that run to finish. Explain that HIGH and CRITICAL scan findings fail the pipeline.

## 4. Infrastructure (about 2 minutes)

Show the Terraform files and the authenticated plan, apply, and destroy evidence in `docs/evidence/`. The AWS cluster and VPC from those screenshots no longer exist. A requirement for a *live* AWS Console view needs a fresh `terraform apply`, then a prompt `terraform destroy` after recording. Review current AWS cost and account permissions before doing that.

## 5. Kubernetes and monitoring (about 3 minutes)

Use the Kind cluster and the instructions in `docs/DEMO.md`. Show `kubectl -n labpulse get pods,svc,ingress,hpa`, `helm list -n labpulse`, and the application through the local Ingress. Open Prometheus Targets and show both backend targets `UP`. Send a few requests to the API, then open the Grafana dashboard and explain the request and latency panels.

## 6. GitOps and closing checks

Open the local Argo CD application and show `Synced` and `Healthy`. The Application points to `main` and renders `helm/labpulse/values-gitops.yaml`. Change the frontend replica count in Git, push, and wait for Argo CD to reconcile three web pods. Recheck the GitHub Actions run, Prometheus targets, and Grafana dashboard. End with the short-lived AWS resource teardown.
