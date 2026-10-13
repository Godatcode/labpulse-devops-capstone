# Demo runbook

Keep two terminals open: one for commands and one for port forwards. The steps below start from the repository root.

## 1. Show the app and tests

```bash
docker compose up --build -d
docker compose ps
curl -fsS http://localhost:8000/health
curl -fsS http://localhost:8000/api/summary
curl -fsS http://localhost:8000/metrics | grep '^http_requests_total' | head
cd backend && .venv/bin/pytest -v && cd ..
```

Open `http://localhost:3000`. Show the overview, filter incidents, and move an incident from open to in progress to resolved. The equipment badge changes with the active incidents.

## 2. Show Kubernetes and Ingress

Follow the Kind setup in the root README. On Kind, the Metrics Server needs this local option because the node's serving certificate is not signed by a trusted CA:

```bash
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
helm upgrade --install metrics-server metrics-server/metrics-server -n kube-system --set 'args[0]=--kubelet-insecure-tls' --wait
kubectl top pods -n labpulse
kubectl get pods,svc,ingress,hpa -n labpulse
helm list -n labpulse
```

The `--kubelet-insecure-tls` setting is for the disposable local Kind cluster. It is not part of the EKS configuration.

In another terminal:

```bash
kubectl -n ingress-nginx port-forward svc/ingress-nginx-controller 8081:80
```

Open `http://localhost:8081` and `http://localhost:8081/api/summary`.

## 3. Show Prometheus and Grafana

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
kubectl create namespace monitoring
kubectl -n monitoring create secret generic grafana-admin \
  --from-literal=admin-user=admin \
  --from-literal=admin-password="$(openssl rand -hex 12)"
helm upgrade --install prometheus prometheus-community/prometheus \
  -n monitoring -f monitoring/prometheus-values.yaml --wait
helm upgrade --install grafana grafana/grafana \
  -n monitoring -f monitoring/grafana-values.yaml --wait
kubectl apply -f monitoring/dashboard-configmap.yaml
```

Forward Prometheus and open `http://localhost:9090/targets`. The `labpulse-backend` target should be UP:

```bash
kubectl -n monitoring port-forward svc/prometheus-server 9090:80
```

In a separate terminal, forward Grafana:

```bash
kubectl -n monitoring port-forward svc/grafana 3001:80
```

Open `http://localhost:3001/d/labpulse-ops/labpulse-c2b7-api-health`. Read the generated admin password from the cluster Secret when prompted:

```bash
kubectl -n monitoring get secret grafana-admin -o jsonpath='{.data.admin-password}' | base64 --decode
```

Generate a few requests against `http://localhost:8081/api/summary` and refresh the dashboard. The request total and route chart should move.

## 4. Explain the pipeline

Open the latest run on [GitHub Actions](https://github.com/Godatcode/labpulse-devops-capstone/actions). Point out the test and frontend jobs, the two Trivy scans, and the SHA image tags. After a small code change passes CI, run `bash scripts/deploy-local.sh` and show the new image tags with `kubectl -n labpulse get deploy -o wide`. The script builds for the local Kind machine, then updates Helm; GitHub Actions publishes the registry images separately.

## 5. Terraform evidence in AWS

The [validation notes](evidence/validation.md) contain both the archived offline plan and the result of an authenticated plan in Sydney (`ap-southeast-2`). Neither is deployment evidence. Before the demo, review the cost and set `admin_cidr` to your current public IP. Apply the reviewed plan, take VPC and EKS Console screenshots and show the managed nodes, then run `terraform destroy` and capture its completion. Keep credentials, state, and plan files out of Git.

## Evidence to capture for the submission

- Browser: Compose at `localhost:3000` and Ingress at `localhost:8081`.
- Terminal: `pytest -v`, `docker compose ps`, `kubectl get pods,svc,hpa`, `helm list`, and `/metrics`.
- GitHub: commit history, green Actions run, and both GHCR packages with SHA tags.
- Monitoring: Prometheus target UP and populated Grafana panel.
- AWS only if actually deployed: plan, Console VPC/EKS, and completed destroy.
