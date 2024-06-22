from math import e
from krs.utils.fetch_tools_krs import krs_tool_ranking_info 
from krs.utils.cluster_scanner import KubetoolsScanner
from krs.utils.llm_client import KrsGPTClient
from krs.utils.functional import extract_log_entries, CustomJSONEncoder
from termcolor import colored
import os, pickle, time, json
from tabulate import tabulate
from krs.utils.constants import (KRSSTATE_PICKLE_FILEPATH, LLMSTATE_PICKLE_FILEPATH, POD_INFO_FILEPATH, KRS_DATA_DIRECTORY)
from krs.utils.log_manager import krs_logger

logger, log_with_exception = krs_logger()

class KrsMain:
    # Class to handle the main functionality of the KRS tool
    
    def __init__(self) -> None:

        """
        Initialize the KrsMain class.
        
        """
        
        try:
            self.pod_info = None
            self.pod_list = None
            self.namespaces = None
            self.deployments = None
            self.state_file = KRSSTATE_PICKLE_FILEPATH
            self.isClusterScanned = False
            self.continue_chat = False
            self.logs_extracted = []
            self.scanner = None
            self.get_events = True
            self.get_logs = True
            self.cluster_tool_list = None
            self.detailed_cluster_tool_list = None
            self.category_cluster_tools_dict = None

            self.load_state()
            
        except Exception as e:
            log_with_exception(f"An error occurred during initialization: {e}", exc_info=True)
            raise e
        except:
            log_with_exception("An error occurred during initialization.", exc_info=True)
            raise Exception("An error occurred during initialization.")


    def initialize(self, config_file : str = '~/.kube/config'):
        
        """
        Initialize the KrsMain class.
        
        Args:
            config_file (str): The path to the kubeconfig file.
        Returns:
            None
        
        """
        
        try:
            self.config_file = config_file
            self.tools_dict, self.category_dict, cncf_status_dict = krs_tool_ranking_info() # Get the tools and their rankings
            self.cncf_status = cncf_status_dict['cncftools'] # Get the CNCF status of the tools
            self.scanner = KubetoolsScanner(self.get_events, self.get_logs, self.config_file) # Initialize the scanner
            self.save_state() # Save the state
        except Exception as e:
            log_with_exception(f"An error occurred during initialization: {e}", exc_info=True)
            raise e
        except:
            log_with_exception("An error occurred during initialization.", exc_info=True)
            raise Exception("An error occurred during initialization.")
        

    def save_state(self) -> None:
        
        """
        
        Save the state of the KrsMain class.
        
        Args:
            None
        Returns:
            None
        
        """
        
        try:
            state = {
                'pod_info': self.pod_info,
                'pod_list': self.pod_list,
                'namespaces': self.namespaces,
                'deployments': self.deployments,
                'cncf_status': self.cncf_status,
                'tools_dict': self.tools_dict,
                'category_tools_dict': self.category_dict,
                'extracted_logs': self.logs_extracted,
                'kubeconfig': self.config_file,
                'isScanned': self.isClusterScanned,
                'cluster_tool_list': self.cluster_tool_list,
                'detailed_tool_list': self.detailed_cluster_tool_list,
                'category_tool_list': self.category_cluster_tools_dict
            }
        except Exception as e:
            log_with_exception(f"An error occurred during saving the state: {e}", exc_info=True)
            raise e
        except:
            log_with_exception("An error occurred during saving the state.", exc_info=True)
            raise Exception("An error occurred during saving the state.")
        
        try:
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True) # Create the directory if it doesn't exist
            with open(self.state_file, 'wb') as f: # Open the file in write mode
                pickle.dump(state, f) # Dump the state to the file
        except Exception as e:
            log_with_exception(f"An error occurred during saving the state: {e}", exc_info=True)
            raise e
        except:
            log_with_exception("An error occurred during saving the state.", exc_info=True)
            raise Exception("An error occurred during saving the state.")


    def load_state(self)-> None:
        
        """
        Load the state of the KrsMain class.
        
        Args:
            None
        Returns:
            None
        """
        
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'rb') as f:
                    state = pickle.load(f)
                    self.pod_info = state.get('pod_info')
                    self.pod_list = state.get('pod_list')
                    self.namespaces = state.get('namespaces')
                    self.deployments = state.get('deployments')
                    self.cncf_status = state.get('cncf_status')
                    self.tools_dict = state.get('tools_dict')
                    self.category_dict = state.get('category_tools_dict')
                    self.logs_extracted = state.get('extracted_logs')
                    self.config_file = state.get('kubeconfig')
                    self.isClusterScanned = state.get('isScanned')
                    self.cluster_tool_list = state.get('cluster_tool_list')
                    self.detailed_cluster_tool_list = state.get('detailed_tool_list')
                    self.category_cluster_tools_dict = state.get('category_tool_list')
                self.scanner = KubetoolsScanner(self.get_events, self.get_logs, self.config_file) # Reinitialize the scanner
        except Exception as e:
            log_with_exception(f"An error occurred during loading the state: {e}", exc_info=True)
            raise e
        except:
            log_with_exception("An error occurred during loading the state.", exc_info=True)
            raise Exception("An error occurred during loading the state.")
        
        
    def check_scanned(self) -> None:
        
        """
        Check if the cluster has been scanned.
        
        Args:
            None
        Returns:
            None
        """
        
        try:
            if not self.isClusterScanned:
                self.pod_list, self.pod_info, self.deployments, self.namespaces = self.scanner.scan_kubernetes_deployment() # Scan the cluster
                self.save_state()
        except Exception as e:
            log_with_exception(f"An error occurred during scanning the cluster: {e}", exc_info=True)
            raise e
        except:
            log_with_exception("An error occurred during scanning the cluster.", exc_info=True)
            raise Exception("An error occurred during scanning the cluster.")
        

    def list_namespaces(self) -> list:
        
        """
        List all the namespaces in the cluster.
        
        Args:
            None
        Returns:
            list: List of namespaces in the cluster.
        """
        try:
            self.check_scanned()
            return self.scanner.list_namespaces()
        except Exception as e:
            log_with_exception(f"An error occurred during listing the namespaces: {e}", exc_info=True)
            raise e
        except:
            log_with_exception("An error occurred during listing the namespaces.", exc_info=True)
            raise Exception("An error occurred during listing the namespaces.")
        
    
    def list_pods(self, namespace: str) -> list:
        
        """ 
        List all the pods in a given namespace.
        
        Args:
            namespace (str): The namespace to list the pods from.
        Returns:
            list: List of pods in the given namespace.
        """
        
        try:
            self.check_scanned()
            if namespace not in self.list_namespaces():
                return "wrong namespace name"
            return self.scanner.list_pods(namespace)
        except Exception as e:
            log_with_exception(f"An error occurred during listing the pods: {e}", exc_info=True)
            raise e
        except:
            log_with_exception("An error occurred during listing the pods.", exc_info=True)
            raise Exception("An error occurred during listing the pods.")
        
    
    def list_pods_all(self) -> list:
        
        """
        list all the pods in the cluster.
        
        Args:
            None
        Returns:
            list: List of all the pods in the cluster.
        """
        
        try:
            self.check_scanned()
            return self.scanner.list_pods_all() # List all the pods in the cluster.
        except Exception as e:
            log_with_exception(f"An error occurred during listing all the pods: {e}", exc_info=True)
            raise e
        except:
            log_with_exception("An error occurred during listing all the pods.", exc_info=True)
            raise Exception("An error occurred during listing all the pods.")
    
    def detect_tools_from_repo(self) -> list:
        
        """
        Detect the tools used in the cluster from the repository.
        
        Args:
            None
        Returns:
            list: List of tools used in the cluster.
        """
        
        try:
            tool_set = set()
            
            # Detect tools from the pods
            for pod in self.pod_list:
                for service_name in pod.split('-'):
                    if service_name in self.tools_dict.keys():
                        tool_set.add(service_name)
                        
            # Detect tools from the deployments
            for dep in self.deployments:
                for service_name in dep.split('-'):
                    if service_name in self.tools_dict.keys():
                        tool_set.add(service_name)
            
            return list(tool_set)
        except Exception as e:
            log_with_exception(f"An error occurred during detecting the tools: {e}", exc_info=True)
            raise e
        except:
            log_with_exception("An error occurred during detecting the tools.", exc_info=True)
            raise Exception("An error occurred during detecting the tools.")
        
    
    def extract_rankings(self) -> tuple:
        
        """
        Extract the rankings of the tools used in the cluster.
        
        Args:
            None
        Returns:
            tuple: A tuple containing the detailed tool list and the category tool list.
        """
        
        try:
            tool_dict = {}
            category_tools_dict = {}
            
            # Extract the rankings of the tools used in the cluster
            for tool in self.cluster_tool_list:
                tool_details = self.tools_dict[tool]
                for detail in tool_details:
                    rank = detail['rank']
                    category = detail['category']
                    if category not in category_tools_dict:
                        category_tools_dict[category] = []
                    category_tools_dict[category].append(rank)

                tool_dict[tool] = tool_details
            
            return tool_dict, category_tools_dict
        except Exception as e:
            log_with_exception(f"An error occurred during extracting the rankings: {e}", exc_info=True)
            raise e
        except:
            log_with_exception("An error occurred during extracting the rankings.", exc_info=True)
            raise Exception("An error occurred during extracting the rankings.")
    
    def generate_recommendations(self) -> None:

        """
        Generate recommendations for the tools used in the cluster.
        
        Args:
            None
        Returns:
            None
        """
        
        try:
            if not self.isClusterScanned:
                self.scan_cluster()

            self.print_recommendations()
        except Exception as e:
            log_with_exception(f"An error occurred during generating recommendations: {e}", exc_info=True)
            raise e
        except:
            log_with_exception("An error occurred during generating recommendations.", exc_info=True)
            raise Exception("An error occurred during generating recommendations.")
    
    
    def scan_cluster(self) -> None:

        """
        Scan the cluster and extract the tools used in the cluster.
        
        Args:
            None
        Returns:
            None
        """

        try:
            print("\nScanning your cluster...\n")
            self.pod_list, self.pod_info, self.deployments, self.namespaces = self.scanner.scan_kubernetes_deployment() # Scan the cluster
            self.isClusterScanned = True
            print("Cluster scanned successfully...\n")
            self.cluster_tool_list = self.detect_tools_from_repo()
            print("Extracted tools used in cluster...\n")
            self.detailed_cluster_tool_list, self.category_cluster_tools_dict = self.extract_rankings() # Extract the rankings of the tools used in the cluster

            self.print_scan_results()
            self.save_state()
        except Exception as e:
            log_with_exception(f"An error occurred during scanning the cluster: {e}", exc_info=True)
            raise e
        except:
            log_with_exception("An error occurred during scanning the cluster.")
            raise Exception("An error occurred during scanning the cluster.")

    def print_scan_results(self) -> None:
        
        """
        Print the scan results of the cluster.
        
        Args:
            None
        Returns:
            None
        """
        
        try:
            scan_results = [] # List to store the scan results

            for tool, details in self.detailed_cluster_tool_list.items(): # Iterate over the tools and their details
                first_entry = True
                for detail in details:
                    row = [tool if first_entry else "", detail['rank'], detail['category'], self.cncf_status.get(tool, 'unlisted')] # Create a row with the tool name, rank, category, and CNCF status
                    scan_results.append(row)
                    first_entry = False

            print("\nThe cluster is using the following tools:\n")
            print(tabulate(scan_results, headers=["Tool Name", "Rank", "Category", "CNCF Status"], tablefmt="grid"))
        except Exception as e:
            log_with_exception(f"An error occurred during printing the scan results: {e}", exc_info=True)
            raise e
        except:
            log_with_exception("An error occurred during printing the scan results.")
            raise Exception("An error occurred during printing the scan results.")

    def print_recommendations(self) -> None:
        
        """
        Print the recommendations for the tools used in the cluster.
        
        Args:
            None
        Returns:
            None
        """
        
        try:
            
            recommendations = []

            for category, ranks in self.category_cluster_tools_dict.items():
                rank = ranks[0]
                recommended_tool = self.category_dict[category][1]['name'] # Get the recommended tool for the category
                status = self.cncf_status.get(recommended_tool, 'unlisted') # Get the CNCF status of the recommended tool
                if rank == 1:
                    row = [category, "Already using the best", recommended_tool, status]
                else:
                    row = [category, "Recommended tool", recommended_tool, status]
                recommendations.append(row)

            print("\nOur recommended tools for this deployment are:\n")
            # Print the recommendations
            print(tabulate(recommendations, headers=["Category", "Recommendation", "Tool Name", "CNCF Status"], tablefmt="grid"))
        except Exception as e:
            log_with_exception(f"An error occurred during printing the recommendations: {e}", exc_info=True)
            raise e
        except:
            log_with_exception("An error occurred during printing the recommendations.", exc_info=True)
            raise Exception("An error occurred during printing the recommendations.")
    
    def health_check(self, change_model: bool = False) -> None:


        """
        Check the health of the cluster, and also start an interactive terminal to chat with the user.
        
        Args:
            change_model (bool): Option to reinitialize/change the LLM.
        Returns:
            None
        """

        try:

            if os.path.exists(LLMSTATE_PICKLE_FILEPATH) and not change_model: # Check if the LLM state file exists and the model is not to be changed
                continue_previous_chat = input("\nDo you want to continue fixing the previously selected pod ? (y/n): >> ")
                while True:
                    if continue_previous_chat not in ['y', 'n']:
                        continue_previous_chat = input("\nPlease enter one of the given options ? (y/n): >> ")
                    else:
                        break

                if continue_previous_chat=='y':
                    krsllmclient = KrsGPTClient() # Initialize the LLM client
                    self.continue_chat = True # Set the continue chat flag to True
                else:
                    krsllmclient = KrsGPTClient(reset_history=True) # Initialize the LLM client
                
            else:
                krsllmclient = KrsGPTClient(reinitialize=True) # Initialize the LLM client
                self.continue_chat = False # Set the continue chat flag to False

            if not self.continue_chat:

                self.check_scanned() # Check if the cluster has been scanned

                print("\nNamespaces in the cluster:\n")
                namespaces = self.list_namespaces()
                namespace_len = len(namespaces)
                for i, namespace in enumerate(namespaces, start=1):
                    print(f"{i}. {namespace}")

                # Select a namespace
                self.selected_namespace_index = int(input("\nWhich namespace do you want to check the health for? Select a namespace by entering its number: >> "))
                while True:
                    if self.selected_namespace_index not in list(range(1, namespace_len+1)):
                        self.selected_namespace_index = int(input(f"\nWrong input! Select a namespace number between {1} to {namespace_len}: >> "))   
                    else:
                        break

                self.selected_namespace = namespaces[self.selected_namespace_index - 1]
                pod_list = self.list_pods(self.selected_namespace)
                pod_len = len(pod_list)
                print(f"\nPods in the namespace {self.selected_namespace}:\n")
                for i, pod in enumerate(pod_list, start=1):
                    print(f"{i}. {pod}")
                self.selected_pod_index = int(input(f"\nWhich pod from {self.selected_namespace} do you want to check the health for? Select a pod by entering its number: >> "))

                while True:
                    if self.selected_pod_index not in list(range(1, pod_len+1)):
                        self.selected_pod_index = int(input(f"\nWrong input! Select a pod number between {1} to {pod_len}: >> "))   
                    else:
                        break

                print("\nChecking status of the pod...")

                print("\nExtracting logs and events from the pod...")

                logs_from_pod = self.get_logs_from_pod(self.selected_namespace_index, self.selected_pod_index)

                self.logs_extracted = extract_log_entries(logs_from_pod)

                print("\nLogs and events from the pod extracted successfully!\n")

            prompt_to_llm = self.create_prompt(self.logs_extracted)

            krsllmclient.interactive_session(prompt_to_llm)

            self.save_state()
        except Exception as e:
            log_with_exception(f"An error occurred during the health check: {e}", exc_info=True)
            raise e
        except:
            log_with_exception("An error occurred during the health check.", exc_info=True)
            raise Exception("An error occurred during the health check.")
        

    def get_logs_from_pod(self, namespace_index: int, pod_index: int) -> list:
        
        """
        Get the logs from a pod.
        
        Args:
            namespace_index (int): The index of the namespace.
            pod_index (int): The index of the pod.
        Returns:
            list: List of logs from the pod.
        """
        
        try:
            namespace_index -= 1
            pod_index -= 1
            namespace = list(self.pod_info.keys())[namespace_index]
            return list(self.pod_info[namespace][pod_index]['info']['Logs'].values())[0]
        except KeyError as e:
            log_with_exception(f"\nKindly enter a value from the available namespaces and pods {e}", exc_info=True)
            return []
        except Exception as e:
            log_with_exception(f"An error occurred during getting logs from the pod: {e}", exc_info=True)
            raise e
        except:
            log_with_exception("An error occurred during getting logs from the pod.", exc_info=True)
            raise Exception("An error occurred during getting logs from the pod.")
        

    def create_prompt(self, log_entries: list) -> str:
            
        """
        Create a prompt for the LLM.
        
        Args:
            log_entries (list): List of log entries.
        Returns:
            str: The prompt for the LLM.
        """
        
        try:
            prompt = "You are a DevOps expert with experience in Kubernetes. Analyze the following log entries:\n{\n"
            for entry in sorted(log_entries):  # Sort to maintain consistent order
                prompt += f"{entry}\n"
            prompt += "}\nIf there is nothing of concern in between { }, return a message stating that 'Everything looks good!'. Explain the warnings and errors and the steps that should be taken to resolve the issues, only if they exist."
            return prompt
        except Exception as e:
            log_with_exception(f"An error occurred during creating the prompt: {e}", exc_info=True)
            raise e
        except:
            log_with_exception("An error occurred during creating the prompt.", exc_info=True)
            raise Exception("An error occurred during creating the prompt.")
        
    
    def export_pod_info(self) -> None:

        """
        Export the pod info with logs and events.
        
        Args:
            None
        Returns:
            None
        """
        
        try:
            self.check_scanned() # Check if the cluster has been scanned

            with open(POD_INFO_FILEPATH, 'w') as f: # Open the file in write mode
                json.dump(self.pod_info, f, cls=CustomJSONEncoder) # Dump the pod info to the file
        except Exception as e:
            log_with_exception(f"An error occurred during exporting the pod info: {e}", exc_info=True)
            raise e
        except:
            log_with_exception("An error occurred during exporting the pod info.", exc_info=True)
            raise Exception("An error occurred during exporting the pod info.")
            

    def exit(self)-> None:

        """
        Exit the tool.
        
        Args:
            None
        Returns:
            None
        """

        try:
            # List all files and directories in the given directory
            files = os.listdir(KRS_DATA_DIRECTORY) # Get all the files in the directory
            for file in files:
                file_path = os.path.join(KRS_DATA_DIRECTORY, file) 
                # Check if it's a file and not a directory
                if os.path.isfile(file_path):
                    os.remove(file_path)  # Delete the file
                    print(f"Deleted file: {file_path}")

        except Exception as e:
            log_with_exception(f"Error occurred: {e}", exc_info=True)
            raise e
        except:
            log_with_exception("An error occurred during deleting the files.", exc_info=True)
            raise Exception("An error occurred during deleting the files.")

    def main(self):
        self.scan_cluster() # Scan the cluster
        self.generate_recommendations() # Generate recommendations
        self.health_check() # Check the health of the cluster
    
    
if __name__=='__main__':
    recommender = KrsMain() # Initialize the KrsMain class
    recommender.main() # Run the main function
    # logs_info = recommender.get_logs_from_pod(4,2)
    # print(logs_info)
    # logs = recommender.extract_log_entries(logs_info)
    # print(logs)
    # print(recommender.create_prompt(logs))

