#!/bin/bash

# Update Helm repository cache
helm repo update

# Install Kubeshark
helm repo add kubeshark https://helm.kubeshark.co
helm install kubeshark kubeshark/kubeshark

## Installing Portainer

kubectl create namespace portainer
helm repo add portainer https://portainer.github.io/k8s/
helm repo update

# Dry run Portainer installation to see what gets installed
helm install --dry-run --debug portainer -n portainer deploy/helm/portainer

# Install Portainer
helm upgrade -i -n portainer portainer portainer/portainer


echo "Kubeshark and Portainer installed successfully!"
