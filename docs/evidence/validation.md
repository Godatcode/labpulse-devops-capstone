# Validation record

Checked on 13–14 and 21 October 2026, using the local Compose stack, a Kind cluster, and short-lived EKS deployments in AWS Sydney. Both AWS deployments were removed after verification.

## Visual evidence

- [LabPulse overview through the local Ingress](labpulse-ingress.jpg)
- [21 October live overview](labpulse-live-overview-2026-10-21.png) and [incident screen](labpulse-live-incidents-2026-10-21.png)
- [LabPulse overview through Docker Compose](labpulse-compose.jpg)
- [Prometheus: both backend targets UP](prometheus-targets.jpg)
- [21 October live Prometheus targets](prometheus-targets-2026-10-21.png)
- [Grafana: request volume, rate, and p95 latency](grafana-dashboard.jpg)
- [21 October live Grafana dashboard](grafana-dashboard-2026-10-21.png)
- [Successful GitHub Actions pipeline](github-actions.jpg)
- [21 October successful push-triggered Actions run](github-actions-2026-10-21.png)
- [Published backend image with SHA tag](ghcr-backend.jpg)
- [Published frontend image with SHA tag](ghcr-frontend.jpg)
- [Meaningful Git commit history](github-history.jpg)
- [AWS EKS cluster active in Sydney](aws-eks-active.jpg)
- [AWS VPC and subnet resource map](aws-vpc-active.jpg)
- [Argo CD application: Synced and Healthy](argocd-synced.png)
- [Presentation deck](../../demo/slides.pdf), [narrated walkthrough](../../demo/walkthrough.mp4), and [captions](../../demo/captions.srt)
- [21 October AWS apply and teardown checks](aws-demo-2026-10-21.txt)

| Check | Result |
| --- | --- |
| Backend unit/API tests | 10 passed against isolated SQLite database |
| Backend lint | `ruff check backend` passed |
| Frontend production build | `npm run build` passed |
| Compose | PostgreSQL and backend healthy; frontend served on port 3000 |
| Compose API | `/api/summary` returned 6 equipment, 2 active reports, 1 resolved report |
| Helm | `helm lint helm/labpulse` passed |
| Kind deployment | PostgreSQL, 2 backend pods, 3 frontend pods Running/Ready after GitOps sync |
| Local Ingress | `localhost:8081/` returned HTML; `/api/summary` returned JSON |
| Terraform init | HashiCorp AWS provider v6.68.0 installed successfully |
| Terraform validate | `Success! The configuration is valid.` |
| Terraform offline plan | `Plan: 24 to add, 0 to change, 0 to destroy.` |
| Terraform AWS plan | Authenticated plan in `ap-southeast-2`: `Plan: 24 to add, 0 to change, 0 to destroy.` |
| Terraform apply | `Apply complete! Resources: 24 added, 0 changed, 0 destroyed.` |
| AWS live checks | EKS cluster and managed node group `ACTIVE`; two `t3.small` nodes `Ready`; VPC and NAT available |
| Terraform destroy | `Destroy complete! Resources: 24 destroyed.` |
| AWS post-destroy checks | No EKS clusters, no LabPulse VPC or Elastic IP; former NAT gateway `deleted`; Terraform state empty |
| HPA metrics | CPU available; backend at 2 replicas with 70% target |
| Prometheus | Two `labpulse-backend` pod targets UP; request count query returned data |
| Grafana | Dashboard `LabPulse · API health` provisioned with 3 panels and Prometheus datasource |
| Argo CD on 21 October | Application tracked `main`, reached `Synced` and `Healthy` at commit `0cdcf607`; changing `frontend.replicas` in Git reconciled the frontend Deployment from 2 to 3 Ready pods |
| GitOps change CI | [Run 39573123517](https://github.com/Godatcode/labpulse-devops-capstone/actions/runs/39573123517) completed successfully: backend tests, frontend build, container build/scan/publish |
| Presentation push CI | [Run 39574857025](https://github.com/Godatcode/labpulse-devops-capstone/actions/runs/39574857025) also completed successfully |
| Presentation | Ten-slide PDF and a 291-second, 1920×1080 H.264 walkthrough with voiceover and on-screen captions are in `demo/` |
| Narrated video CI example | [Run 39595649955](https://github.com/Godatcode/labpulse-devops-capstone/actions/runs/39595649955) completed successfully after the recorded push of `e89dc05` |

The offline plan used Terraform 1.16.5 with a reserved documentation IP and fake local credentials. Provider identity checks were skipped using `offline_plan=true`; no AWS API calls or resources were involved:

```bash
docker run --rm \
  -e AWS_ACCESS_KEY_ID=offline \
  -e AWS_SECRET_ACCESS_KEY=offline \
  -e AWS_EC2_METADATA_DISABLED=true \
  -v "$PWD/terraform:/workspace" -w /workspace \
  hashicorp/terraform:1.16.5 plan -refresh=false -input=false -no-color \
  -var=admin_cidr=203.0.113.1/32 -var=offline_plan=true
```

The full archived offline output is in [terraform-offline-plan.txt](terraform-offline-plan.txt). On 14 October, the AWS CLI profile authenticated successfully. EKS and VPC read calls worked in `ap-southeast-2`; the account had no EKS clusters there. Terraform validated and produced a fresh plan against the account with two `t3.small` workers and a restricted API CIDR. The saved plan and its exact CIDR are local and excluded from Git. Terraform then applied the plan. The [AWS deployment log](aws-deployment.txt) records the live CLI and Kubernetes checks. The [teardown log](aws-destroy.txt) records the completed destroy and independent post-destroy checks.

On 21 October, the account was authenticated again and Terraform repeated the `24 to add` plan and apply. AWS reported the EKS cluster `ACTIVE`; `kubectl` reported both managed workers `Ready`. Terraform then destroyed all 24 resources. Independent AWS queries returned no EKS cluster, no tagged LabPulse VPC, and no tagged NAT Elastic IP; Terraform state listed zero resources. The [second deployment record](aws-demo-2026-10-21.txt) captures those results.

The local command outputs are in [tests.txt](tests.txt), [compose.txt](compose.txt), and [kubernetes.txt](kubernetes.txt). The [GitOps change CI run](https://github.com/Godatcode/labpulse-devops-capstone/actions/runs/39573123517) shows tests, builds, scans, and publication. Both SHA-tagged GHCR manifests were accessible from Docker without a GHCR login.

Trivy scanned Alpine OS packages in both runtime images and Python libraries in the backend. The first frontend scan found 43 HIGH findings in an older Nginx base; after moving to the current slim unprivileged image, the successful run reported zero HIGH/CRITICAL findings for both images. The gate still exits with a failure if a new HIGH or CRITICAL issue appears.
