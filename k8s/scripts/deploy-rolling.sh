#!/bin/bash
# Rolling update: replace pods gradually; roll back automatically if anything fails
set -euo pipefail
NEW_IMAGE="$IMAGE:$APP_VERSION"
URL="http://192.168.49.2:30080"

kubectl apply -f k8s/rolling-update/service.yaml
kubectl set image deployment/aceest-fitness aceest-fitness="$NEW_IMAGE"
kubectl annotate deployment/aceest-fitness --overwrite \
  kubernetes.io/change-cause="Jenkins build ${BUILD_NUMBER:-manual}: version $APP_VERSION"

if ! kubectl rollout status deployment/aceest-fitness --timeout=120s \
   || ! curl -fs "$URL/version" | grep -q "\"$APP_VERSION\""; then
  echo "Rolling update failed - rolling back to the previous version"
  kubectl rollout undo deployment/aceest-fitness
  kubectl rollout status deployment/aceest-fitness --timeout=120s
  exit 1
fi
echo "Rolling update to $APP_VERSION succeeded"
