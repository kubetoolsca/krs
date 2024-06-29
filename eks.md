# Install and Configure Krs with EKS (AWS)


## Prerequisites

- AWS Account
- AWSCLI installed on your system
- Homebrew(if you're on Mac)


## Getting Started

### 1. Setup Amazon EKS Cluster

```
$ eksctl create cluster --name <cluster_name> --version <kubernetes_version> --region <aws_region_name e.g us-east-1> --nodegroup-name <linux_nodes> --node-type <node_type>  --nodes <number_of_nodes> --zones=<zone_names, e.g: us-east-1a,us-east-1b>
```



![EKS_Clusters](https://github.com/kubetoolsca/krs/assets/171302280/edd250c6-12d6-4380-b430-302b06c98a73)


### 2. Authenticate your AWS account 

   
   ```
   aws configure 
   ```



### 3. Extract the list of running clusters on AWS using this command:
   
```
$ aws eks list-clusters
```

### 4. Create a config file that permits KRS access to the EKS cluster using this command:<br><be>

```
aws eks update-kubeconfig --name <cluster_name> 
```


### 5. Setup KRS using these commands:<br><be>

```
$git clone https://github.com/kubetoolsca/krs.git
$ cd krs
$ pip install
```

### 6. Initialize KRS to permit it access to your cluster using the given command,<br><be>

```
krs init
```

### 7. Get a view of all possible actions with KRS, by running the given command <br><be>


```
krs --help
                                                                                
 Usage: krs [OPTIONS] COMMAND [ARGS]...                                         
                                                                                
 krs: A command line interface to scan your Kubernetes Cluster, detect errors,  
 provide resolutions using LLMs and recommend latest tools for your cluster     
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.      │
│ --show-completion             Show completion for the current shell, to copy │
│                               it or customize the installation.              │
│ --help                        Show this message and exit.                    │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ exit         Ends krs services safely and deletes all state files from       │
│              system. Removes all cached data.                                │
│ export       Exports pod info with logs and events.                          │
│ health       Starts an interactive terminal using an LLM of your choice to   │
│              detect and fix issues with your cluster                         │
│ init         Initializes the services and loads the scanner.                 │
│ namespaces   Lists all the namespaces.                                       │
│ pods         Lists all the pods with namespaces, or lists pods under a       │
│              specified namespace.                                            │
│ recommend    Generates a table of recommended tools from our ranking         │
│              database and their CNCF project status.                         │
│ scan         Scans the cluster and extracts a list of tools that are         │
│              currently used.                                                 │
╰──────────────────────────────────────────────────────────────────────────────╯
```

### 8. Permit KRS to get information on the tools utilized in your cluster by running the given command <br><be>

```
   krs scan

   Scanning your cluster...
   
   Cluster scanned successfully...
   
   Extracted tools used in cluster...
   
   The cluster is using the following tools:
   
   +-------------+--------+-----------------------------+---------------+
   | Tool Name   |   Rank | Category                    | CNCF Status   |
   +=============+========+=============================+===============+
   | autoscaler  |      5 | Cluster with Core CLI tools | unlisted      |
   +-------------+--------+-----------------------------+---------------+
   | istio       |      2 | Service Mesh                | graduated     |
   +-------------+--------+-----------------------------+---------------+
   | kserve      |      3 | Artificial Intelligence     | listed        |
   +-------------+--------+-----------------------------+---------------+
```

#### 9. Get recommendations on possible tools to use in your cluster by running the given command <br><be>

```
   krs recommend
   ```
   ```
      +-----------------------------+------------------+-------------+---------------+
   | Category                    | Recommendation   | Tool Name   | CNCF Status   |
   +=============================+==================+=============+===============+
   | Cluster with Core CLI tools | Recommended tool | k9s         | unlisted      |
   +-----------------------------+------------------+-------------+---------------+
   | Service Mesh                | Recommended tool | traefik     | listed        |
   +-----------------------------+------------------+-------------+---------------+
   | Artificial Intelligence     | Recommended tool | k8sgpt      | sandbox       |
   +-----------------------------+------------------+-------------+---------------+
```

#### 10. Check the pod and namespace status in your Kubernetes cluster, including errors. 

```
   krs health
   ```
   ```
   Starting interactive terminal...

Choose the model provider for healthcheck: 

[1] OpenAI 
[2] Huggingface

>> 1

Installing necessary libraries..........

openai is already installed.

Enter your OpenAI API key: sk-proj-xxxxxxxxxx

Enter the OpenAI model name: gpt-3.5-turbo
API key and model are valid.

Namespaces in the cluster:

1. cert-manager
2. default
3. istio-system
4. knative-serving
5. kserve
6. kserve-test
7. kube-node-lease
8. kube-public
9. Kube-system

Which namespace do you want to check the health for? Select a namespace by entering its number: >> 9

Pods in the namespace kube-system:

1. aws-node-46hzm
2. aws-node-wdgnn
3. coredns-586b798467-54t6h
4. coredns-586b798467-jmlrp
5. kube-proxy-hfmjl
6. kube-proxy-n8lc6

Which pod from kube-system do you want to check the health for? Select a pod by entering its number: >> 1

Checking status of the pod...

Extracting logs and events from the pod...

Logs and events from the pod extracted successfully!


Interactive session started. Type 'end chat' to exit from the session!

>>  The provided log entries are empty, so there is nothing to analyze. Everything looks good!

>> Wonderful, so what next
>>  If you have any specific questions or another set of log entries you would like me to analyze, feel free to provide them. I'm here to help with any DevOps or Kubernetes-related queries you may have. Just let me know how I can assist you further!
```







