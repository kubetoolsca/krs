# Install and Configure Krs with EKS (AWS)

## Goals

- Setting up a fully connected EKS cluster
- Permitting your local machine access to a running EKS cluster
- Interacting with your cluster through KRS

## Prerequisites

- AWS account
- Linux CLI
- Kubectl installation

## Setting up a fully connected EKS cluster

![EKS_Clusters](https://github.com/kubetoolsca/krs/assets/171302280/edd250c6-12d6-4380-b430-302b06c98a73)

1. Install Homebrew in your system using this command:<br>
   ```
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
   Then, run the following commands to complete its setup:<br>
  ```
  (echo; echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"') >> /home/oluchukwu/.bashrc
  eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"

  ```
3.
  
