#!/bin/bash

# Function to uninstall a Helm release
uninstall_helm_release() {
  local release_name="$1"
  helm uninstall "$release_name" || true  # Suppress errors if release not found
}

# Update Helm repository cache
helm repo update


# Uninstall Kubeshark
uninstall_helm_release kubeshark

# Uninstall Portainer
uninstall_helm_release portainer

## deleting the namespaces
kubectl delete ns portainer
kubectl delete ns kubeshark

echo "Kubeshark and Portainer uninstalled (if previously installed)."
