# Validation record

Checked on 13 October 2026, using the local Compose stack and a Kind cluster. The AWS plan below is offline.

| Check | Result |
| --- | --- |
| Backend unit/API tests | 10 passed against isolated SQLite database |
| Backend lint | `ruff check backend` passed |
| Frontend production build | `npm run build` passed |
| Compose | PostgreSQL and backend healthy; frontend served on port 3000 |
| Compose API | `/api/summary` returned 6 equipment, 2 active reports, 1 resolved report |
| Helm | `helm lint helm/labpulse` passed |
| Kind deployment | PostgreSQL, 2 backend pods, 2 frontend pods Running/Ready |
| Local Ingress | `localhost:8081/` returned HTML; `/api/summary` returned JSON |
| Terraform init | HashiCorp AWS provider v6.68.0 installed successfully |
| Terraform validate | `Success! The configuration is valid.` |
| Terraform offline plan | `Plan: 24 to add, 0 to change, 0 to destroy.` |
| HPA metrics | CPU available; backend at 2 replicas with 70% target |
| Prometheus | Two `labpulse-backend` pod targets UP; request count query returned data |
| Grafana | Dashboard `LabPulse · API health` provisioned with 3 panels and Prometheus datasource |

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

The full output is in [terraform-offline-plan.txt](terraform-offline-plan.txt). There is no real EKS provisioning or destroy evidence because no AWS account credentials are configured.
