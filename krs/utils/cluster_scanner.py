from kubernetes import client, config
import logging

class KubetoolsScanner:
    def __init__(self, get_events=True, get_logs=True, config_file='~/.kube/config'):
        self.get_events = get_events
        self.get_logs = get_logs
        self.config_file = config_file
        self.v1 = None
        self.v2 = None
        self.setup_kubernetes_client()

    def setup_kubernetes_client(self):
        """
        Sets up the Kubernetes client using the provided kubeconfig file.
        """
        try:
            config.load_kube_config(config_file=self.config_file)
            self.v1 = client.AppsV1Api()
            self.v2 = client.CoreV1Api()
            logging.info("Kubernetes client setup completed successfully.")
        except Exception as e:
            logging.error("Failed to load Kubernetes configuration: %s", e)
            raise

    def scan_kubernetes_deployment(self):
        """
        Scans the Kubernetes cluster for deployments, namespaces, and pods.

        Returns:
            tuple: A tuple containing lists of pod names, pod information, deployment names, and namespaces.
        """
        try:
            logging.info("Starting Kubernetes deployment scan.")
            deployments = self.v1.list_deployment_for_all_namespaces()
            namespaces = self.list_namespaces()
        except Exception as e:
            logging.error("Error fetching data from Kubernetes API: %s", e)
            return [], {}, [], []

        pod_dict = {}
        pod_list = []
        for name in namespaces:
            pods = self.list_pods(name)
            pod_list.extend(pods)
            pod_dict[name] = [{'name': pod, 'info': self.get_pod_info(name, pod)} for pod in pods]

        deployment_list = [dep.metadata.name for dep in deployments.items]
        logging.info("Kubernetes deployment scan completed successfully.")
        return pod_list, pod_dict, deployment_list, namespaces

    def list_namespaces(self):
        """
        Lists all namespaces in the Kubernetes cluster.

        Returns:
            list: A list of namespace names.
        """
        try:
            namespaces = self.v2.list_namespace()
            logging.info("Fetched namespaces successfully.")
            return [namespace.metadata.name for namespace in namespaces.items]
        except Exception as e:
            logging.error("Error fetching namespaces: %s", e)
            return []

    def list_pods_all(self):
        """
        Lists all pods across all namespaces in the Kubernetes cluster.

        Returns:
            list: A list of pod names.
        """
        try:
            pods = self.v2.list_pod_for_all_namespaces()
            logging.info("Fetched all pods successfully.")
            return [pod.metadata.name for pod in pods.items]
        except Exception as e:
            logging.error("Error fetching all pods: %s", e)
            return []

    def list_pods(self, namespace):
        """
        Lists all pods in a specific namespace.

        Args:
            namespace (str): The namespace to list pods from.

        Returns:
            list: A list of pod names in the specified namespace.
        """
        try:
            pods = self.v2.list_namespaced_pod(namespace)
            logging.info("Fetched pods for namespace '%s' successfully.", namespace)
            return [pod.metadata.name for pod in pods.items]
        except Exception as e:
            logging.error("Error fetching pods for namespace '%s': %s", namespace, e)
            return []

    def get_pod_info(self, namespace, pod):
        """
        Retrieves detailed information about a specific pod.

        Args:
            namespace (str): The namespace of the pod.
            pod (str): The name of the pod.

        Returns:
            dict: A dictionary containing the pod information, events, and logs.
        """
        try:
            pod_info = self.v2.read_namespaced_pod(pod, namespace)
            pod_info_map = pod_info.to_dict()
            pod_info_map["metadata"]["managed_fields"] = None  # Clean up metadata

            info = {'PodInfo': pod_info_map}

            if self.get_events:
                info['Events'] = self.fetch_pod_events(namespace, pod)

            if self.get_logs:
                info['Logs'] = self.fetch_pod_logs(namespace, pod, pod_info)

            logging.info("Fetched information for pod '%s' in namespace '%s' successfully.", pod, namespace)
            return info
        except Exception as e:
            logging.error("Error fetching pod info for pod '%s' in namespace '%s': %s", pod, namespace, e)
            return {}

    def fetch_pod_events(self, namespace, pod):
        """
        Fetches events related to a specific pod.

        Args:
            namespace (str): The namespace of the pod.
            pod (str): The name of the pod.

        Returns:
            list: A list of events related to the specified pod.
        """
        try:
            events = self.v2.list_namespaced_event(namespace)
            logging.info("Fetched events for pod '%s' in namespace '%s' successfully.", pod, namespace)
            return [{'Name': event.metadata.name, 'Message': event.message, 'Reason': event.reason}
                    for event in events.items if event.involved_object.name == pod]
        except Exception as e:
            logging.error("Error fetching events for pod '%s' in namespace '%s': %s", pod, namespace, e)
            return []

    def fetch_pod_logs(self, namespace, pod, pod_info):
        """
        Fetches logs for all containers within a specific pod.

        Args:
            namespace (str): The namespace of the pod.
            pod (str): The name of the pod.
            pod_info (V1Pod): The pod information object.

        Returns:
            dict: A dictionary with container names as keys and their logs as values.
        """
        container_logs = {}
        for container in pod_info.spec.containers:
            try:
                logs = self.v2.read_namespaced_pod_log(name=pod, namespace=namespace, container=container.name)
                container_logs[container.name] = logs
                logging.info("Fetched logs for container '%s' in pod '%s' successfully.", container.name, pod)
            except Exception as e:
                logging.error("Failed to fetch logs for container '%s' in pod '%s': %s", container.name, pod, e)
                container_logs[container.name] = "Error fetching logs: " + str(e)
        return container_logs


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    scanner = KubetoolsScanner()
    pod_list, pod_info, deployments, namespaces = scanner.scan_kubernetes_deployment()
    print("POD List: \n\n", pod_list)
    print("\n\nPOD Info: \n\n", pod_info.keys())
    print("\n\nNamespaces: \n\n", namespaces)
    print("\n\nDeployments: \n\n", deployments)
