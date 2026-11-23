#!/bin/bash
# Blue-green: deploy to the idle colour, test it, then switch live traffic in one step
set -euo pipefail
NEW_IMAGE="$IMAGE:$APP_VERSION"
LIVE_URL="http://192.168.49.2:30081"
PREVIEW_URL="http://192.168.49.2:30082"

switch_service() {   # $1 = service name, $2 = colour
  kubectl patch service "$1" -p "{\"spec\":{\"selector\":{\"app\":\"aceest-bg\",\"color\":\"$2\"}}}"
}

# Create the blue-green objects only if they don't exist yet (never reset a live setup)
kubectl get service aceest-bg >/dev/null 2>&1 || kubectl apply -f k8s/blue-green/

LIVE=$(kubectl get service aceest-bg -o jsonpath='{.spec.selector.color}')
if [ "$LIVE" = "blue" ]; then IDLE=green; else IDLE=blue; fi
echo "Live colour: $LIVE - deploying $APP_VERSION to idle colour: $IDLE"

kubectl set image "deployment/aceest-$IDLE" aceest-fitness="$NEW_IMAGE"
kubectl rollout status "deployment/aceest-$IDLE" --timeout=120s

# Test the idle colour through the preview service before it gets real traffic
switch_service aceest-bg-preview "$IDLE"
sleep 3
if ! curl -fs "$PREVIEW_URL/version" | grep -q "\"$APP_VERSION\""; then
  echo "Preview check failed - live traffic was never switched"
  exit 1
fi

# Switch live traffic in one step
switch_service aceest-bg "$IDLE"
sleep 3
if ! curl -fs "$LIVE_URL/version" | grep -q "\"$APP_VERSION\""; then
  echo "Live check failed - switching back to $LIVE"
  switch_service aceest-bg "$LIVE"
  exit 1
fi
echo "Blue-green done: live traffic is on $IDLE ($APP_VERSION); $LIVE kept for instant rollback"
