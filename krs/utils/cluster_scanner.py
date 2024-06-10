from math import e
from kubernetes import client, config
import logging


# Define the KubetoolsScanner class
class KubetoolsScanner:
    
    
    def __init__(self, get_events: bool = True, get_logs: bool =True, config_file: str ='~/.kube/config') -> None:
        """
        __init__ method for the KubetoolsScanner class.
        
        Args:
            get_events (bool): Flag indicating whether to fetch events associated with the pod.
            get_logs (bool): Flag indicating whether to fetch logs of the pod.
            config_file (str): The path to the Kubernetes configuration file.
        
        Returns:
            None
        
        """
        self.get_events = get_events
        self.get_logs = get_logs
        self.config_file = config_file
        self.v1 = None
        self.v2 = None
        self.setup_kubernetes_client()

    def setup_kubernetes_client(self) -> None:
        
        """
        Sets up the Kubernetes client using the configuration file provided.
        
        Args:
            None
            
        Returns:
            None
            
        """
        
        try:
            # Load the Kubernetes configuration
            config.load_kube_config(config_file=self.config_file) # Load the Kubernetes configuration
            self.v1 = client.AppsV1Api() # Create an instance of the Kubernetes AppsV1 API
            self.v2 = client.CoreV1Api() # Create an instance of the Kubernetes CoreV1 API
        except Exception as e:
            logging.error("Failed to load Kubernetes configuration: %s", e)
            raise
        except:
            logging.error("An error occurred while setting up the Kubernetes client.")
            raise

    def scan_kubernetes_deployment(self) -> tuple:
        
        """
        Scans the Kubernetes deployment for pods, deployments, and namespaces.
        
        Args:
            None
        Returns:
            tuple: A tuple containing the list of pods, pod information, deployments, and namespaces.
        
        """
        
        try:
            
            # Fetch the list of pods, pod information, deployments, and namespaces
            deployments = self.v1.list_deployment_for_all_namespaces() # Fetch deployments
            namespaces = self.list_namespaces()
            
            pod_dict = {}
            pod_list = []
            for name in namespaces:
                pods = self.list_pods(name)
                pod_list += pods
                pod_dict[name] = [{'name': pod, 'info': self.get_pod_info(name, pod)} for pod in pods] # Fetch pod info

            # Extract the names of the pods and deployments
            deployment_list = [dep.metadata.name for dep in deployments.items] # List deployment names
            return pod_list, pod_dict, deployment_list, namespaces # Return the list of pods, pod info, deployments, and namespaces
        
        except client.rest.ApiException as e:
            logging.error("Error fetching data from Kubernetes API: %s", e)
            return [], {}, [], []
        except Exception as e:
            logging.error("Error fetching data from Kubernetes API: %s", e)
            return {}, {}, []
        except:
            logging.error("An error occurred while fetching data from the Kubernetes API.")
            return {}, {}, []


    def list_namespaces(self) -> list:
        
        """  
        Lists all the namespaces in the Kubernetes cluster.

        Args:
            None
        
        Returns:
            list: A list of namespace names.
        """
        
        try:
            namespaces = self.v2.list_namespace() # List all namespaces
            return [namespace.metadata.name for namespace in namespaces.items] # Extract namespace names
        except Exception as e:
            logging.error("Failed to list namespaces: %s", e)
            return []
        except:
            logging.error("An error occurred while listing namespaces.")
            return []
    
    def list_pods_all(self) -> list:
        
        """
        Lists all the pods in all namespaces in the Kubernetes cluster.
        
        Args:
            None
        
        Returns:
            list: A list of pod names.
        """
        
        try:
            pods = self.v2.list_pod_for_all_namespaces() # List all pods
            return [pod.metadata.name for pod in pods.items] # Extract pod names
        except Exception as e:
            logging.error("Failed to list pods: %s", e)
            return []
        except:
            logging.error("An error occurred while listing pods.")
            return []

    def list_pods(self, namespace : str) -> list:
        
        try:
            pods = self.v2.list_namespaced_pod(namespace) # List pods in a specific namespace
            return [pod.metadata.name for pod in pods.items] # Extract pod names
        except Exception as e:
            logging.error("Failed to list pods in namespace %s: %s", namespace, e)
            return []
        except:
            logging.error("An error occurred while listing pods in namespace %s.", namespace)
            return []

    def get_pod_info(self, namespace : str, pod: str, include_events: bool =True, include_logs: bool = True) -> dict:
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
        
        try:
            
            # Fetch pod information
            pod_info = self.v2.read_namespaced_pod(pod, namespace) # Read pod information
            pod_info_map = pod_info.to_dict() # Convert to dictionary
            pod_info_map["metadata"]["managed_fields"] = None  # Clean up metadata

            info = {'PodInfo': pod_info_map}
            
            if include_events:
                info['Events'] = self.fetch_pod_events(namespace, pod)
            
            if include_logs:
                # Retrieve logs for all containers within the pod
                container_logs = {}
                
                # Fetch logs for each container in the pod
                for container in pod_info.spec.containers:
                    try:
                        logs = self.v2.read_namespaced_pod_log(name=pod, namespace=namespace, container=container.name) # Read logs
                        container_logs[container.name] = logs # Store logs in a dictionary
                    except Exception as e:
                        logging.error("Failed to fetch logs for container %s in pod %s: %s", container.name, pod, e)
                        container_logs[container.name] = "Error fetching logs: " + str(e)
                info['Logs'] = container_logs

            return info
        except client.rest.ApiException as e:
            logging.error("Error fetching pod info: %s", e)
            return {}
        except Exception as e:
            logging.error("Error fetching pod info: %s", e)
            return {}
        except:
            logging.error("An error occurred while fetching pod info.")
            return {}

    def fetch_pod_events(self, namespace: str, pod: str) -> list:
        
        """
        Fetches the events associated with a specific pod in a given namespace.
        
        Args:
            namespace (str): The namespace of the pod.
            pod (str): The name of the pod.
            
        Returns:
            list: A list of event details.
            
        """
        
        try:
            events = self.v2.list_namespaced_event(namespace)
            return [{
                'Name': event.metadata.name,
                'Message': event.message,
                'Reason': event.reason
            } for event in events.items if event.involved_object.name == pod]
        except client.rest.ApiException as e:
            logging.error("Error fetching events for pod %s in namespace %s: %s", pod, namespace, e)
            return []
        except Exception as e:
            logging.error("Error fetching events for pod %s in namespace %s: %s", pod, namespace, e)
            return []
        except:
            logging.error("An error occurred while fetching events for pod %s in namespace %s.", pod, namespace)
            return []


if __name__ == '__main__':

    scanner = KubetoolsScanner() # Initialize the KubetoolsScanner
    pod_list, pod_info, deployments, namespaces = scanner.scan_kubernetes_deployment() # Scan the Kubernetes deployment
    print("POD List: \n\n", pod_list)
    print("\n\nPOD Info: \n\n", pod_info.keys())
    print("\n\nNamespaces: \n\n", namespaces)
    print("\n\nDeployments : \n\n", deployments)

