#!/bin/bash
# Canary: send a growing share of traffic to the new version; promote it only if healthy
set -euo pipefail
NEW_IMAGE="$IMAGE:$APP_VERSION"
URL="http://192.168.49.2/version"
HOST="canary.aceest.local"

set_weight() {
  kubectl annotate ingress canary-new --overwrite nginx.ingress.kubernetes.io/canary-weight="$1"
}

# Create the canary objects only if they don't exist yet
kubectl get ingress canary-new >/dev/null 2>&1 || kubectl apply -f k8s/progressive/ -f k8s/canary/

kubectl set image deployment/aceest-new aceest-fitness="$NEW_IMAGE"
kubectl rollout status deployment/aceest-new --timeout=120s

for WEIGHT in 10 50 100; do
  set_weight "$WEIGHT"
  sleep 5
  FAILED=0
  NEW=0
  for _ in $(seq 50); do
    RESPONSE=$(curl -fs -H "Host: $HOST" "$URL") || FAILED=$((FAILED + 1))
    if echo "$RESPONSE" | grep -q "\"$APP_VERSION\""; then NEW=$((NEW + 1)); fi
  done
  echo "Canary at $WEIGHT%: $NEW/50 requests answered by $APP_VERSION, $FAILED failed"
  if [ "$FAILED" -gt 0 ]; then
    echo "Errors at $WEIGHT% - rolling back: canary weight set to 0"
    set_weight 0
    exit 1
  fi
done

# Promote: the new version becomes the stable one, then close the canary
kubectl set image deployment/aceest-stable aceest-fitness="$NEW_IMAGE"
kubectl rollout status deployment/aceest-stable --timeout=120s
set_weight 0
echo "Canary promoted: stable is now $APP_VERSION"
