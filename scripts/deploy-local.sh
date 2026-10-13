#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

if [[ -n "$(git status --porcelain)" ]]; then
  echo "Commit the current changes before deploying a SHA-tagged build." >&2
  exit 2
fi
revision="$(git rev-parse --short=12 HEAD)"

cluster_name="${KIND_CLUSTER:-labpulse}"
kube_context="${KUBE_CONTEXT:-kind-$cluster_name}"

docker build -q -t "labpulse-backend:$revision" backend
docker build -q -t "labpulse-frontend:$revision" frontend
kind load docker-image "labpulse-backend:$revision" "labpulse-frontend:$revision" --name "$cluster_name"

helm upgrade --install labpulse helm/labpulse \
  -n labpulse --kube-context "$kube_context" --reuse-values \
  --set-string image.backend.repository=labpulse-backend \
  --set-string image.backend.tag="$revision" \
  --set-string image.frontend.repository=labpulse-frontend \
  --set-string image.frontend.tag="$revision" \
  --set ingress.host=localhost \
  --wait --timeout 5m

kubectl --context "$kube_context" -n labpulse rollout status deployment/labpulse-backend --timeout=3m
kubectl --context "$kube_context" -n labpulse rollout status deployment/labpulse-frontend --timeout=3m
kubectl --context "$kube_context" -n labpulse get pods

echo "LabPulse $revision is running in the $cluster_name Kind cluster."
