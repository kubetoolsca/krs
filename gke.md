## Setting up Krs for Google Kubernetes Engine

## Prerequisite

- A Google Cloud Account
- Installing Google Cloud SDK on your macOS

Execute the following command to install Google Cloud SDK in your system:

```
tar xfz google-cloud-sdk-195.0.0-darwin-x86_64.tar.gz
./google-cloud-sdk/install.sh
```


- Enable Google Cloud Engine API

![image](https://github.com/kubetoolsca/krs/assets/313480/6c441226-9e8e-4a91-ba8a-e0c595173faa)


- Authenticate Your Google Cloud using gcloud auth


```
gcloud init
```

In your browser, log in to your Google user account when prompted and click Allow to grant permission to access Google Cloud Platform resources.


## Creating GKE Cluster

```
gcloud container clusters create k8s-lab1 --disk-size 10 --zone asia-east1-a --machine-type n1-standard-2 --num-nodes 3 --scopes compute-rw
```

## Viewing it on Google Cloud Platform

![image](https://github.com/kubetoolsca/krs/assets/313480/733cfe3a-c951-4ea0-b7f5-4a28f7393c8e)


## Viewing the new context on Docker Desktop

<img width="738" alt="image" src="https://github.com/kubetoolsca/krs/assets/313480/8afc21c5-1961-4af8-b491-00c99cb350fa">

### Verifying the Google Kubernetes Cluster 

```
kubectl get nodes
NAME                                      STATUS   ROLES    AGE    VERSION
gke-k8s-lab1-default-pool-5dfb7153-3fr7   Ready    <none>   3m1s   v1.29.4-gke.1043002
gke-k8s-lab1-default-pool-5dfb7153-nl3v   Ready    <none>   3m1s   v1.29.4-gke.1043002
gke-k8s-lab1-default-pool-5dfb7153-rkg8   Ready    <none>   3m2s   v1.29.4-gke.1043002
```

## Initialize the KRS

```
krs init
Services initialized and scanner loaded.
```

## Running the scanner

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
| fluentbit   |      4 | Logging and Tracing         | unlisted      |
+-------------+--------+-----------------------------+---------------+
```

## Checking the Krs Recommendation

```
krs recommend

Our recommended tools for this deployment are:

+-----------------------------+------------------+-------------+---------------+
| Category                    | Recommendation   | Tool Name   | CNCF Status   |
+=============================+==================+=============+===============+
| Cluster with Core CLI tools | Recommended tool | k9s         | unlisted      |
+-----------------------------+------------------+-------------+---------------+
| Logging and Tracing         | Recommended tool | elk         | unlisted      |
```


## Installing Kubeview

```
git clone https://github.com/benc-uk/kubeview
cd kubeview/charts/
helm install kubeview kubeview
```

## Running the scanner again

```
krs scan

Scanning your cluster...

Cluster scanned successfully...

Extracted tools used in cluster...


The cluster is using the following tools:

+-------------+--------+-----------------------------+---------------+
| Tool Name   |   Rank | Category                    | CNCF Status   |
+=============+========+=============================+===============+
| kubeview    |     30 | Cluster with Core CLI tools | unlisted      |
+-------------+--------+-----------------------------+---------------+
|             |      3 | Cluster Management          | unlisted      |
+-------------+--------+-----------------------------+---------------+
| autoscaler  |      5 | Cluster with Core CLI tools | unlisted      |
+-------------+--------+-----------------------------+---------------+
| fluentbit   |      4 | Logging and Tracing         | unlisted      |
+-------------+--------+-----------------------------+---------------+
```
