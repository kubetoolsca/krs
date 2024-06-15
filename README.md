<img width="117" alt="image" src="https://github.com/KrsGPTs/krs/assets/313480/582cf437-5dcf-4039-9c59-397db6e8b644">

![Twitter](https://img.shields.io/twitter/follow/kubetools?style=social)

# Kubetools Recommender System

A GenAI-powered Python-based Kubetools Recommender system for your Kubernetes cluster. 

# Table of Contents

- [Kubetools Recommender System](#kubetools-recommender-system)
- [Getting Started](#getting-started)
  - [Clone the repository](#clone-the-repository)
  - [Install the Krs Tool](#install-the-krs-tool)
  - [Krs CLI](#krs-cli)
- [Initialise and load the scanner](#initialise-and-load-the-scanner)
- [Scan your cluster](#scan-your-cluster)
- [Lists all the namespaces](#lists-all-the-namespaces)
- [Installing sample Kubernetes Tools](#installing-sample-kubernetes-tools)
- [Use scanner](#use-scanner)
- [Kubetools Recommender System](#kubetools-recommender-system-1)
- [Krs health](#krs-health)
  - [Using OpenAI](#using-openai)
  - [Using Hugging Face](#using-hugging-face)# Kubetools Recommender System



The main functionalities of the project include:

<img width="1499" alt="image" src="https://github.com/kubetoolsca/krs/assets/313480/14fa0beb-2203-4ab4-b34b-d90888584177">


- Scanning the Kubernetes cluster: The tool scans the cluster to identify the deployed pods, services, and deployments. It retrieves information about the tools used in the cluster and their rankings.
- Detecting tools from the repository: The tool detects the tools used in the cluster by analyzing the names of the pods and deployments.
- Extracting rankings: The tool extracts the rankings of the detected tools based on predefined criteria. It categorizes the tools into different categories and provides the rankings for each category.
- Generating recommendations: The tool generates recommendations for Kubernetes tools based on the detected tools and their rankings. It suggests the best tools for each category and compares them with the tools already used in the cluster.
- Health check: The tool provides a health check for a selected pod in the cluster. It extracts logs and events from the pod and analyzes them using a language model (LLM) to identify potential issues and provide recommendations for resolving them.
- Exporting pod information: The tool exports the information about the pods, services, and deployments in the cluster to a JSON file.
- Cleaning up: The tool provides an option to clean up the project's data directory by deleting all files and directories within it.
- Supports OpenAI and Hugging Face models

The project uses various Python libraries, such as typer, requests, kubernetes, tabulate, and pickle, to accomplish its functionalities. 
It also utilizes a language model (LLM) for the health check feature. 
The project's directory structure and package management are managed using requirements.txt. 
The project's data, such as tool rankings, CNCF status, and Kubernetes cluster information, are stored in JSON files and pickled files.

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

The user is prompted to choose a model provider for the health check. 
The options provided are "OpenAI" and "Huggingface". The selected option determines which LLM model will be used for the health check.

Let's say you choose the option "1", then it will install the necessary libraries.


```
Enter your OpenAI API key: sk-3iXXXXXTpTyyOq2mR

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


## Using Hugging Face

```
krs health

Starting interactive terminal...


Choose the model provider for healthcheck:

[1] OpenAI
[2] Huggingface

>> 2

Installing necessary libraries..........

transformers is already installed.

torch is already installed.
/opt/homebrew/lib/python3.11/site-packages/transformers/utils/generic.py:311: UserWarning: torch.utils._pytree._register_pytree_node is deprecated. Please use torch.utils._pytree.register_pytree_node instead.
  torch.utils._pytree._register_pytree_node(

Enter the Huggingface model name: codellama/CodeLlama-13b-hf
tokenizer_config.json: 100%|█████████████████████████████████████████████| 749/749 [00:00<00:00, 768kB/s]
tokenizer.model: 100%|████████████████████████████████████████████████| 500k/500k [00:00<00:00, 1.94MB/s]
tokenizer.json: 100%|███████████████████████████████████████████████| 1.84M/1.84M [00:01<00:00, 1.78MB/s]
special_tokens_map.json: 100%|██████████████████████████████████████████| 411/411 [00:00<00:00, 1.49MB/s]
config.json: 100%|██████████████████████████████████████████████████████| 589/589 [00:00<00:00, 1.09MB/s]
model.safetensors.index.json: 100%|█████████████████████████████████| 31.4k/31.4k [00:00<00:00, 13.9MB/s]
...
```









