# Local GitOps demo

Argo CD watches the public `main` branch and renders `helm/labpulse` using `values-gitops.yaml`. This setup runs in a local Kind cluster. The chart uses images loaded into the Kind node; GitHub Actions publishes separate SHA-tagged images to GHCR.

On a fresh Kind cluster, build and load the local images before creating the Application:

```bash
kind create cluster --name labpulse
docker build -t labpulse-backend:22aa496b517c backend
docker build -t labpulse-frontend:22aa496b517c frontend
kind load docker-image labpulse-backend:22aa496b517c labpulse-frontend:22aa496b517c --name labpulse
kubectl create namespace labpulse
kubectl -n labpulse create secret generic labpulse-db --from-literal=password=labpulse-local-only
```

Install Argo CD using its official Kubernetes manifest, then create the Application:

```bash
kubectl create namespace argocd
kubectl apply -n argocd --server-side --force-conflicts -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl -n argocd rollout status deployment/argocd-server --timeout=5m
kubectl apply -f gitops/application.yaml
kubectl -n argocd get application labpulse
```

For a visible GitOps change, edit `frontend.replicas` in `values-gitops.yaml`, commit and push the change, and watch Argo CD reconcile it. `kubectl -n labpulse get deploy labpulse-frontend` shows the new replica count. The Argo CD web UI can be reached with `kubectl -n argocd port-forward svc/argocd-server 8082:443`; its initial admin password is in the `argocd-initial-admin-secret` Secret. Keep that password out of the recording.

The existing Helm installation used for the original Kubernetes evidence is present in the same local cluster. Argo CD now reconciles the chart from Git. Avoid running a separate Helm upgrade against the same release while demonstrating Argo CD.
