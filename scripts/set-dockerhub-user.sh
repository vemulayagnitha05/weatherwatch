#!/usr/bin/env sh
# Usage: ./scripts/set-dockerhub-user.sh <your-dockerhub-username>
# Updates the image references in the Kubernetes Deployments and the Makefile in one go.
set -e
[ -n "$1" ] || { echo "usage: $0 <dockerhub-username>"; exit 1; }
cd "$(dirname "$0")/.."
sed -i.bak -E "s#image: [A-Za-z0-9_.-]+/weatherwatch-(api|collector):#image: $1/weatherwatch-\1:#" \
  k8s/api-deployment.yaml k8s/collector-deployment.yaml
sed -i.bak -E "s#^DOCKERHUB_USER \?= .*#DOCKERHUB_USER ?= $1#" Makefile
rm -f k8s/*.bak Makefile.bak
grep -n "image:" k8s/api-deployment.yaml k8s/collector-deployment.yaml
