# LabPulse walkthrough

The [captioned video](walkthrough.mp4) runs for about two minutes. It opens with the [presentation slides](slides.pdf), then shows the application, repository structure, latest successful CI run, AWS evidence, live command output, Argo CD, Prometheus, and Grafana. Captions are burned into the MP4, so it can be watched without audio.

## Demo sequence

1. Introduce the equipment register and its React → FastAPI → PostgreSQL path.
2. Show the application through the local Ingress and the repository directories.
3. Show the successful push-triggered GitHub Actions run: tests, frontend build, container build, Trivy scan, and GHCR publication.
4. Explain the Terraform VPC and EKS resources. The video includes AWS Console captures and live AWS CLI and Kubernetes checks from the short-lived deployment.
5. Show Argo CD `Synced` and `Healthy`; the Git change to `frontend.replicas` brought the local Deployment to `3/3` Ready.
6. Show both Prometheus backend targets `UP` and the Grafana request and latency panels.
7. Close with the project's limits and AWS cleanup. The Terraform stack was destroyed after the evidence was captured.

The command output in the video was recorded against the real local Kind cluster and AWS account. The older Console screenshots in `docs/evidence/` show the same Terraform stack during its first live deployment. The 21 October CLI footage shows the second apply. For exact commands, see [the local demo runbook](../docs/DEMO.md), [GitOps setup](../gitops/README.md), and [validation record](../docs/evidence/validation.md).
