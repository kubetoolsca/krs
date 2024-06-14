# Kubetools Recommender System


<img width="117" alt="image" src="https://github.com/KrsGPTs/krs/assets/313480/582cf437-5dcf-4039-9c59-397db6e8b644">

![Twitter](https://img.shields.io/twitter/follow/kubetools?style=social)

A GenAI-powered Python-based Kubetools Recommender system for your Kubernetes cluster. 
The main functionalities of the project include:

- Scanning the Kubernetes cluster: The tool scans the cluster to identify the deployed pods, services, and deployments. It retrieves information about the tools used in the cluster and their rankings.
- Detecting tools from the repository: The tool detects the tools used in the cluster by analyzing the names of the pods and deployments.
- Extracting rankings: The tool extracts the rankings of the detected tools based on predefined criteria. It categorizes the tools into different categories and provides the rankings for each category.
- Generating recommendations: The tool generates recommendations for Kubernetes tools based on the detected tools and their rankings. It suggests the best tools for each category and compares them with the tools already used in the cluster.
- Health check: The tool provides a health check for a selected pod in the cluster. It extracts logs and events from the pod and analyzes them using a language model (LLM) to identify potential issues and provide recommendations for resolving them.
- Exporting pod information: The tool exports the information about the pods, services, and deployments in the cluster to a JSON file.
- Cleaning up: The tool provides an option to clean up the project's data directory by deleting all files and directories within it.
- Supports OpenAI and Hugging Face models

<img width="300" alt="image" src="https://github.com/KrsGPTs/krs/assets/313480/ea071bb8-1282-4b06-8bb6-01f082e4cce0">


## Prerequisites:

1. A Kubernetes cluster up and running locally or in the Cloud. 
2. Python 3.6+

Note: If the kube config path for your cluster is not the default *(~/.kube/config)*, ensure you are providing it during `krs init`

## Tested Environment

- Docker Desktop(Mac, Linux and Windows)
- Minikube
- [Google Kubernetes Engine](https://github.com/kubetoolsca/krs/blob/main/gke.md)


## Getting Started


## Clone the repository

```
git clone https://github.com/kubetoolsca/krs.git
```

### Install the Krs Tool

Change directory to /krs and run the following command to install krs locally on your system:

```
pip install .
````


## Krs CLI

```

 krs --help

 Usage: krs [OPTIONS] COMMAND [ARGS]...

 krs: A command line interface to scan your Kubernetes Cluster, detect errors, provide resolutions using LLMs and recommend latest tools for your cluster

╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                                                                                       │
│ --show-completion             Show completion for the current shell, to copy it or customize the installation.                                                │
│ --help                        Show this message and exit.                                                                                                     │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ exit         Ends krs services safely and deletes all state files from system. Removes all cached data.                                                       │
│ export       Exports pod info with logs and events.                                                                                                           │
│ health       Starts an interactive terminal using an LLM of your choice to detect and fix issues with your cluster                                            │
│ init         Initializes the services and loads the scanner.                                                                                                  │
│ namespaces   Lists all the namespaces.                                                                                                                        │
│ pods         Lists all the pods with namespaces, or lists pods under a specified namespace.                                                                   │
│ recommend    Generates a table of recommended tools from our ranking database and their CNCF project status.                                                  │
│ scan         Scans the cluster and extracts a list of tools that are currently used.                                                                          │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## Initialise and load the scanner

Run the following command to initialize the services and loads the scanner.


```
krs init
```

## Scan your cluster 

Run the following command to scan the cluster and extract a list of tools that are currently used.

```
krs scan
```

You will see the following results:

```

Scanning your cluster...

Cluster scanned successfully...

Extracted tools used in cluster...


The cluster is using the following tools:

+-------------+--------+------------+---------------+
| Tool Name   | Rank   | Category   | CNCF Status   |
+=============+========+============+===============+
+-------------+--------+------------+---------------+
```


## Lists all the namespaces

```
krs namespaces
Namespaces in your cluster are:

1. default
2. kube-node-lease
3. kube-public
4. kube-system
```

## Installing sample Kubernetes Tools

Assuming that you already have a bunch of Kubernetes tools running in your infrastructure.
If not, you can leverage [samples/install-tools.sh](samples/install-tools.sh) script to install these sample tools.

```
cd samples
sh install-tools.sh
```

## Use scanner 

```
krs scan

Scanning your cluster...

Cluster scanned successfully...

Extracted tools used in cluster...


The cluster is using the following tools:

+-------------+--------+----------------------+---------------+
| Tool Name   |   Rank | Category             | CNCF Status   |
+=============+========+======================+===============+
| kubeshark   |      4 | Alert and Monitoring | unlisted      |
+-------------+--------+----------------------+---------------+
| portainer   |     39 | Cluster Management   | listed        |
+-------------+--------+----------------------+---------------+
```

## Kubetools Recommender System

Generates a table of recommended tools from our ranking database and their CNCF project status.


```
krs recommend

Our recommended tools for this deployment are:

+----------------------+------------------+-------------+---------------+
| Category             | Recommendation   | Tool Name   | CNCF Status   |
+======================+==================+=============+===============+
| Alert and Monitoring | Recommended tool | grafana     | listed        |
+----------------------+------------------+-------------+---------------+
| Cluster Management   | Recommended tool | rancher     | unlisted      |
+----------------------+------------------+-------------+---------------+
```


## Krs health


Assuming that there is a Nginx Pod under the namespace ns1

```
krs pods --namespace ns1

Pods in namespace 'ns1':

1. nginx-pod
```

```
krs health

Starting interactive terminal...


Choose the model provider for healthcheck:

[1] OpenAI
[2] Huggingface

>>
```

Let's say you choose 1, the it will install necessary libraries.


```
Enter your OpenAI API key: sk-3im1ZgCbKXXXXXXXXegTpTyyOq2mR

Enter the OpenAI model name: gpt-3.5-turbo
API key and model are valid.

Namespaces in the cluster:

1. default
2. kube-node-lease
3. kube-public
4. kube-system
5. ns1

Which namespace do you want to check the health for? Select a namespace by entering its number: >> 5

Pods in the namespace ns1:

1. nginx-pod

Which pod from ns1 do you want to check the health for? Select a pod by entering its number: >>
Checking status of the pod...

Extracting logs and events from the pod...

Logs and events from the pod extracted successfully!


Interactive session started. Type 'end chat' to exit from the session!

>>  The provided log entries are empty, as there is nothing between the curly braces {}. Therefore, everything looks good and there are no warnings or errors to report.
```









