# Kubetools Recommender System


<img width="117" alt="image" src="https://github.com/KrsGPTs/krs/assets/313480/582cf437-5dcf-4039-9c59-397db6e8b644">

![Twitter](https://img.shields.io/twitter/follow/kubetools?style=social)

A GenAI-powered Kubetools Recommender system for your Kubernetes cluster. It comes with the following capabilities:

- Ability to scan your existing Kubernetes cluster 
- Available in the form of CLI tool as well as listed on the [Kubetools](https://kubetools.io) webpage
- Ability to recommend you with the best tool and categories based on your running workloads
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

### Install the Tool

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


## List pods under a specified namespace

Assuming that there is a Nginx Pod under the namespace ns1

```
krs pods --namespace ns1

Pods in namespace 'ns1':

1. nginx-pod
```

## krs recommend

Generates a table of recommended tools from our ranking database and their CNCF project status.

```
krs recommend

Our recommended tools for this deployment are:

+-----------------------------+------------------+-------------+---------------+
| Category                    | Recommendation   | Tool Name   | CNCF Status   |
+=============================+==================+=============+===============+
| Cluster with Core CLI tools | Recommended tool | k9s         | unlisted      |
+-----------------------------+------------------+-------------+---------------+
| Cluster Management          | Recommended tool | rancher     | unlisted      |
+-----------------------------+------------------+-------------+---------------+
```

## Krs health

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









