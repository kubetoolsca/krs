from krs.utils.fetch_tools_krs import krs_tool_ranking_info
from krs.utils.cluster_scanner import KubetoolsScanner
from krs.utils.llm_client import KrsGPTClient
from krs.utils.functional import extract_log_entries, CustomJSONEncoder
import os, pickle, time, json
from tabulate import tabulate
from krs.utils.constants import (KRSSTATE_PICKLE_FILEPATH, LLMSTATE_PICKLE_FILEPATH, POD_INFO_FILEPATH, KRS_DATA_DIRECTORY)

class KrsMain:
    
    def __init__(self):

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

    def initialize(self, config_file='~/.kube/config'):
        self.config_file = config_file
        self.tools_dict, self.category_dict, cncf_status_dict = krs_tool_ranking_info()
        self.cncf_status = cncf_status_dict['cncftools']
        self.scanner = KubetoolsScanner(self.get_events, self.get_logs, self.config_file)
        self.save_state()

    def save_state(self):
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
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'wb') as f:
            pickle.dump(state, f)

    def load_state(self):
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
            self.scanner = KubetoolsScanner(self.get_events, self.get_logs, self.config_file)
    
    def check_scanned(self):
        if not self.isClusterScanned:
            self.pod_list, self.pod_info, self.deployments, self.namespaces = self.scanner.scan_kubernetes_deployment()
            self.save_state()

    def list_namespaces(self):
        self.check_scanned()
        return self.scanner.list_namespaces()
    
    def list_pods(self, namespace):
        self.check_scanned()
        if namespace not in self.list_namespaces():
            return "wrong namespace name"
        return self.scanner.list_pods(namespace)
    
    def list_pods_all(self):
        self.check_scanned()
        return self.scanner.list_pods_all()
    
    def detect_tools_from_repo(self):
        tool_set = set()
        for pod in self.pod_list:
            for service_name in pod.split('-'):
                if service_name in self.tools_dict.keys():
                    tool_set.add(service_name)
        
        for dep in self.deployments:
            for service_name in dep.split('-'):
                if service_name in self.tools_dict.keys():
                    tool_set.add(service_name)
        
        return list(tool_set)
    
    def extract_rankings(self):
        tool_dict = {}
        category_tools_dict = {}
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
    
    def generate_recommendations(self):

        if not self.isClusterScanned:
            self.scan_cluster()

        self.print_recommendations()
    
    def scan_cluster(self):

        print("\nScanning your cluster...\n")
        self.pod_list, self.pod_info, self.deployments, self.namespaces = self.scanner.scan_kubernetes_deployment()
        self.isClusterScanned = True
        print("Cluster scanned successfully...\n")
        self.cluster_tool_list = self.detect_tools_from_repo()
        print("Extracted tools used in cluster...\n")
        self.detailed_cluster_tool_list, self.category_cluster_tools_dict = self.extract_rankings()

        self.print_scan_results()
        self.save_state()

    def print_scan_results(self):
        scan_results = []

        for tool, details in self.detailed_cluster_tool_list.items():
            first_entry = True
            for detail in details:
                row = [tool if first_entry else "", detail['rank'], detail['category'], self.cncf_status.get(tool, 'unlisted')]
                scan_results.append(row)
                first_entry = False

        print("\nThe cluster is using the following tools:\n")
        print(tabulate(scan_results, headers=["Tool Name", "Rank", "Category", "CNCF Status"], tablefmt="grid"))

    def print_recommendations(self):
        recommendations = []

        for category, ranks in self.category_cluster_tools_dict.items():
            rank = ranks[0]
            recommended_tool = self.category_dict[category][1]['name']
            status = self.cncf_status.get(recommended_tool, 'unlisted')
            if rank == 1:
                row = [category, "Already using the best", recommended_tool, status]
            else:
                row = [category, "Recommended tool", recommended_tool, status]
            recommendations.append(row)

        print("\nOur recommended tools for this deployment are:\n")
        print(tabulate(recommendations, headers=["Category", "Recommendation", "Tool Name", "CNCF Status"], tablefmt="grid"))

    
    def health_check(self, change_model=False, device='cpu'):

        if os.path.exists(LLMSTATE_PICKLE_FILEPATH) and not change_model:
            continue_previous_chat = input("\nDo you want to continue fixing the previously selected pod ? (y/n): >> ")
            while True:
                if continue_previous_chat not in ['y', 'n']:
                    continue_previous_chat = input("\nPlease enter one of the given options ? (y/n): >> ")
                else:
                    break

            if continue_previous_chat=='y':
                krsllmclient = KrsGPTClient(device=device)
                self.continue_chat = True
            else:
                krsllmclient = KrsGPTClient(reset_history=True, device=device)
            
        else:
            krsllmclient = KrsGPTClient(reinitialize=True, device=device)
            self.continue_chat = False

        if not self.continue_chat:

            self.check_scanned()

            print("\nNamespaces in the cluster:\n")
            namespaces = self.list_namespaces()
            namespace_len = len(namespaces)
            for i, namespace in enumerate(namespaces, start=1):
                print(f"{i}. {namespace}")

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

    def get_logs_from_pod(self, namespace_index, pod_index):
        try:
            namespace_index -= 1
            pod_index -= 1
            namespace = list(self.list_namespaces())[namespace_index]
            return list(self.pod_info[namespace][pod_index]['info']['Logs'].values())[0]
        except KeyError as e:
            print("\nKindly enter a value from the available namespaces and pods")
            return None

    def create_prompt(self, log_entries):
        prompt = "You are a DevOps expert with experience in Kubernetes. Analyze the following log entries:\n{\n"
        for entry in sorted(log_entries):  # Sort to maintain consistent order
            prompt += f"{entry}\n"
        prompt += "}\nIf there is nothing of concern in between { }, return a message stating that 'Everything looks good!'. Explain the warnings and errors and the steps that should be taken to resolve the issues, only if they exist."
        return prompt
    
    def export_pod_info(self):

        self.check_scanned()

        with open(POD_INFO_FILEPATH, 'w') as f:
            json.dump(self.pod_info, f, cls=CustomJSONEncoder)
            

    def exit(self):

        try:
            # List all files and directories in the given directory
            files = os.listdir(KRS_DATA_DIRECTORY)
            for file in files:
                file_path = os.path.join(KRS_DATA_DIRECTORY, file)
                # Check if it's a file and not a directory
                if os.path.isfile(file_path):
                    os.remove(file_path)  # Delete the file
                    print(f"Deleted file: {file_path}")

        except Exception as e:
            print(f"Error occurred: {e}")

    def main(self):
        self.scan_cluster()
        self.generate_recommendations()
        self.health_check()
    
    
if __name__=='__main__':
    recommender = KrsMain()
    recommender.main()
    # logs_info = recommender.get_logs_from_pod(4,2)
    # print(logs_info)
    # logs = recommender.extract_log_entries(logs_info)
    # print(logs)
    # print(recommender.create_prompt(logs))

