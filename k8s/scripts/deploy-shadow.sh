#!/bin/bash
# Shadow: run the new version on a copy of live traffic; users keep getting the stable version
set -euo pipefail
NEW_IMAGE="$IMAGE:$APP_VERSION"
URL="http://192.168.49.2/version"
HOST="shadow.aceest.local"

# Create the shadow objects only if they don't exist yet
kubectl get ingress shadow-main >/dev/null 2>&1 || kubectl apply -f k8s/progressive/ -f k8s/shadow/

kubectl set image deployment/aceest-shadow aceest-fitness="$NEW_IMAGE"
kubectl rollout status deployment/aceest-shadow --timeout=120s
sleep 5

echo "What users receive (stable version):"
for _ in $(seq 10); do curl -fs -H "Host: $HOST" "$URL"; done

sleep 2
MIRRORED=$(kubectl logs -l app=aceest-shadow --since=30s --tail=-1 | grep -c "GET /version" || true)
echo "Shadow ($APP_VERSION) received $MIRRORED mirrored requests"
kubectl logs -l app=aceest-shadow --since=30s --tail=-1 --prefix | grep "GET /version" || true
