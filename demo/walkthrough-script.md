# LabPulse video narration

## 01 · Introduction

LabPulse is a small operations tracker for shared lab equipment. This walkthrough follows the working app, the delivery pipeline, the AWS deployment evidence, and the monitoring setup.

## 02 · The product

The overview shows six instruments and the reports that affect their status. A technician can open an incident, move a repair into progress, and resolve it. The equipment badge follows the active reports.

## 03 · Architecture

The browser reaches an Nginx frontend. Requests under API go to FastAPI, which stores equipment and incidents in PostgreSQL. The same backend exports Prometheus metrics, so the dashboard reflects real requests.

## 04 · Repository tour

The repository is split by responsibility: backend, frontend, Helm, Terraform, GitOps, and monitoring. The API tests sit beside the backend code. The deployment and dashboard configuration are versioned with the application.

## 05 · Key files

The workflow defines the quality gate. The Helm chart supplies Deployments, Services, Ingress, and an autoscaler. Terraform defines the AWS network and EKS cluster. Each part can be reviewed without searching through one large file.

## 06 · Push to main

Here is a real push to the main branch. GitHub Actions starts from that commit, so the pipeline result can be tied to a specific version of the repository.

## 07 · CI and image publication

The backend job lints and tests the API, while the frontend job checks formatting and builds production assets. Only after both pass does the container job build, scan with Trivy, and publish SHA-tagged images to GitHub Container Registry.

## 08 · Terraform plan

Terraform planned twenty-four AWS resources in Sydney: a two-zone VPC, public and private subnets, NAT routing, EKS, and a managed node group. The plan was reviewed before the short-lived deployment.

## 09 · AWS network

In the AWS Console capture, the VPC resource map shows the two public and two private subnets. The private subnets hold the worker nodes, while routing and NAT provide controlled outbound access.

## 10 · EKS verification

The EKS cluster reached Active, the node group reached Active, and Kubernetes reported two Ready workers. This Console capture is from the earlier live deployment of the same Terraform stack; the later CLI verification is preserved in the evidence log.

## 11 · GitOps with Argo CD

Argo CD watches the main branch and renders the Helm chart for the local Kind cluster. A committed replica change was reconciled automatically. The application showed Synced and Healthy, and the frontend reached three Ready replicas.

## 12 · Kubernetes health

The local cluster has healthy backend and frontend pods, PostgreSQL, three Services, an Nginx Ingress, and a backend autoscaler. The API summary also responds through the Ingress, confirming the route from browser to service.

## 13 · Prometheus

Prometheus discovers both backend pods, and both targets are Up. The API exposes request counts and latency at its metrics endpoint, which gives the monitoring stack application data rather than only container health.

## 14 · Grafana

The Grafana dashboard shows requests handled, request rate by route, and ninety-fifth percentile response time. After traffic is sent through the app, those panels display data from Prometheus.

## 15 · Cleanup

The AWS environment was kept only long enough to verify it. Terraform destroyed all twenty-four resources. Separate AWS checks found no LabPulse EKS cluster, VPC, or reserved NAT address left behind.

## 16 · Closing

The result is a working app with tests, a guarded delivery pipeline, a demonstrated cloud deployment, GitOps reconciliation, and observable API traffic. The repository includes the exact setup steps and evidence for each part.
