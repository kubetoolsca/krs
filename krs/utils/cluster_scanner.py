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
        try:
            config.load_kube_config(config_file=self.config_file)
            self.v1 = client.AppsV1Api()
            self.v2 = client.CoreV1Api()
        except Exception as e:
            logging.error("Failed to load Kubernetes configuration: %s", e)
            raise

    def scan_kubernetes_deployment(self):
        try:
            deployments = self.v1.list_deployment_for_all_namespaces()
            namespaces = self.list_namespaces()
        except Exception as e:
            logging.error("Error fetching data from Kubernetes API: %s", e)
            return {}, {}, []

        pod_dict = {}
        pod_list = []
        for name in namespaces:
            pods = self.list_pods(name)
            pod_list += pods
            pod_dict[name] = [{'name': pod, 'info': self.get_pod_info(name, pod)} for pod in pods]

        deployment_list = [dep.metadata.name for dep in deployments.items]
        return pod_list, pod_dict, deployment_list, namespaces

    def list_namespaces(self):
        namespaces = self.v2.list_namespace()
        return [namespace.metadata.name for namespace in namespaces.items]
    
    def list_pods_all(self):
        pods = self.v2.list_pod_for_all_namespaces()
        return [pod.metadata.name for pod in pods.items]

    def list_pods(self, namespace):
        pods = self.v2.list_namespaced_pod(namespace)
        return [pod.metadata.name for pod in pods.items]

    def get_pod_info(self, namespace, pod, include_events=True, include_logs=True):
        """
        Retrieves information about a specific pod in a given namespace.

        Args:
            namespace (str): The namespace of the pod.
            pod (str): The name of the pod.
            include_events (bool): Flag indicating whether to include events associated with the pod.
            include_logs (bool): Flag indicating whether to include logs of the pod.

        Returns:
            dict: A dictionary containing the pod information, events (if include_events is True), and logs (if include_logs is True).
        """
        pod_info = self.v2.read_namespaced_pod(pod, namespace)
        pod_info_map = pod_info.to_dict()
        pod_info_map["metadata"]["managed_fields"] = None  # Clean up metadata

        info = {'PodInfo': pod_info_map}
        
        if include_events:
            info['Events'] = self.fetch_pod_events(namespace, pod)
        
        if include_logs:
            # Retrieve logs for all containers within the pod
            container_logs = {}
            for container in pod_info.spec.containers:
                try:
                    logs = self.v2.read_namespaced_pod_log(name=pod, namespace=namespace, container=container.name)
                    container_logs[container.name] = logs
                except Exception as e:
                    logging.error("Failed to fetch logs for container %s in pod %s: %s", container.name, pod, e)
                    container_logs[container.name] = "Error fetching logs: " + str(e)
            info['Logs'] = container_logs

        return info

    def fetch_pod_events(self, namespace, pod):
        events = self.v2.list_namespaced_event(namespace)
        return [{
            'Name': event.metadata.name,
            'Message': event.message,
            'Reason': event.reason
        } for event in events.items if event.involved_object.name == pod]


if __name__ == '__main__':

    scanner = KubetoolsScanner()
    pod_list, pod_info, deployments, namespaces = scanner.scan_kubernetes_deployment()
    print("POD List: \n\n", pod_list)
    print("\n\nPOD Info: \n\n", pod_info.keys())
    print("\n\nNamespaces: \n\n", namespaces)
    print("\n\nDeployments : \n\n", deployments)

