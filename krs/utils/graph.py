#Author: Oluchukwu Obi-Njoku
#Date: 8-26-2024
#Description: Kubernetes cluster graph generating program



import subprocess
import sys
import json
from krs.utils.constants import (SUPER_GRAPH_PATH, GRAPH_DATA_PATH, SUBGRAPH_PATH,SUBGRAPH_NAMESPACES_PATH,SUBGRAPH_POD_PATH)


def create_super_graph() -> dict:

    """
    Create a graph representation of the Kubernetes cluster and write it to a file
    
    Args:
        None
    Returns:
        dict
    """

    try:
        output = run_command("kubectl get all --all-namespaces -o json") # Run the command
        if(output):
            write_output_to_file(GRAPH_DATA_PATH, output) # Write the output to a file
            graph = create_graph_data(GRAPH_DATA_PATH) # Create the graph data
            write_output_to_file(SUPER_GRAPH_PATH, json.dumps(graph)) # Write the graph data to a file
            return graph
    except subprocess.TimeoutExpired:
        print(f"Timeout expired for: kubectl get all --all-namespaces -o json")
        return {"Error" : "Timeout expired for: kubectl get all --all-namespaces -o json"}
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e}")
        return {"Error" : f"Command failed with error: {e}"}
    except FileNotFoundError as e:
        print(f"Command failed with error: {e}")
        return {"Error" : f"Command failed with error: {e}"}
    except OSError as e:
        print(f"Command failed with error: {e}")
        return {"Error" : f"Command failed with error: {e}"}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"Error" : f"Command failed with error: {e}"}
    except:
        print(f"An error occurred.")
        return {"Error" : f"Error Occurred"}
    

def write_output_to_file(filename: str, input: str) -> None:

    """
    Write the output of a command to a file

    Args:
        filename (str): The name of the file to write to
        output (str): The output to write to the file
    Returns:
        None
    """

    try:
        with open(filename, "w") as f:
                f.write(input)
    except FileNotFoundError as e:
        print(f"Command failed with error: {e}")
        sys.exit(1)
    except OSError as e:
        print(f"Command failed with error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
    except:
        print(f"An error occurred.")
        sys.exit(1)


def run_command(command_str:str, retries:int = 3, timeout: int =120) -> bool:

    """
    Run a command in the shell

    Args: 
        command_str (str): The command to run
        retries (int): The number of times to retry the command
        timeout (int): The timeout for the command

    Returns: bool: True if the command was successful, False otherwise
    """

    try:

        for attempt in range(retries):
            try:

                print(f"Running: {command_str} (Attempt {attempt + 1}/{retries})")
                result = subprocess.run(command_str, shell=True, capture_output=True, check=True, timeout=timeout, text=True)
                print(f"Completed: {command_str}")
                return result.stdout
                #return result.returncode == 0

            except subprocess.TimeoutExpired:
                print(f"Timeout expired for: {command_str}")            
                return False

            except subprocess.CalledProcessError as e:
                print(f"Command failed with error: {e}")            
                return False

            except FileNotFoundError as e:
                print(f"Command failed with error: {e}")            
                return False

            except OSError as e:
                print(f"Command failed with error: {e}")            
                return False

            except Exception as e:
                print(f"Command failed with error: {e}")            
                return False

            except:
                print(f"Command failed.")            
                return False
            
            # time.sleep(5)  # Wait before retrying

        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    except:
        print(f"An error occurred.")
        return False


def create_graph_data(filename: str) -> dict:

    """
    Create a graph representation of the Kubernetes cluster

    Args:
        filename (str): The name of the file containing the cluster data
    Returns:
        dict: A dictionary representing the graph
    """

    try:
        with open(filename, "r") as f:
            data = json.load(f)

        graph = {"nodes": [], "edges": []}

        # Add nodes and edges based on the cluster data
        for item in data['items']:
            kind = item['kind']
            metadata = item['metadata']
            name = metadata['name']
            namespace = metadata.get('namespace', 'default')

            node_id = f"{namespace}/{name}"
            node_data = {
                "id": node_id,
                "kind": kind,
                "namespace": namespace,
                "name": name,
                "status": item.get('status', {}),
                "labels": metadata.get('labels', {}),
                "annotations": metadata.get('annotations', {}),
            }
            graph["nodes"].append(node_data)

            # Add edges based on ownerReferences
            owner_references = metadata.get('ownerReferences', [])
            for owner in owner_references:
                owner_name = owner['name']
                owner_namespace = namespace  # Assuming owner is in the same namespace
                owner_id = f"{owner_namespace}/{owner_name}"
                graph["edges"].append({"source": owner_id, "target": node_id})

        return graph
    except FileNotFoundError as e:
        print(f"Command failed with error: {e}")
        sys.exit(1)
    except OSError as e:
        print(f"Command failed with error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
    except:
        print(f"An error occurred.")
        sys.exit(1)

def identify_error_prone_nodes(filename: str) -> list:
    """
    Identify error-prone nodes in the Kubernetes cluster.

    Args:
        filename (str): The name of the file containing the cluster data.

    Returns:
        list: A list of error-prone nodes with their details.
    """

    try:
        with open(filename, "r") as f:
            data = json.load(f)

        error_prone_nodes = []

        for node in data['nodes']:
            node_status = node.get('status', {})
            conditions = node_status.get('conditions', [])
            container_statuses = node_status.get('containerStatuses', [])

            # Check for conditions where status is not "True"
            for condition in conditions:
                if condition['status'] != "True":
                    error_prone_nodes.append({
                        "id": node['id'],
                        "kind": node['kind'],
                        "namespace": node['namespace'],
                        "name": node['name'],
                        "condition_type": condition['type'],
                        "condition_status": condition['status'],
                        "last_transition_time": condition['lastTransitionTime']
                    })

            # Check for container statuses with errors
            for container_status in container_statuses:
                last_state = container_status.get('lastState', {})
                if 'terminated' in last_state and last_state['terminated'].get('reason') == "Error":
                    error_prone_nodes.append({
                        "id": node['id'],
                        "kind": node['kind'],
                        "namespace": node['namespace'],
                        "name": node['name'],
                        "container_name": container_status['name'],
                        "error_reason": last_state['terminated']['reason'],
                        "exit_code": last_state['terminated']['exitCode'],
                        "finished_at": last_state['terminated']['finishedAt']
                    })

        return error_prone_nodes
    except FileNotFoundError as e:
        print(f"Command failed with error: {e}")
        sys.exit(1)
    except OSError as e:
        print(f"Command failed with error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
    except:
        print(f"An error occurred.")
        sys.exit(1)

def create_subgraph(main_graph_filename: str, subgraph_filename: str, error_nodes: list) -> dict:
    """
    Create a subgraph from the main graph based on error-prone nodes.

    Args:
        main_graph_filename (str): The name of the file containing the main graph data.
        subgraph_filename (str): The name of the file to write the subgraph data.
        error_nodes (list): A list of error-prone nodes.

    Returns:
        dict
    """

    try:
        with open(main_graph_filename, "r") as f:
            main_graph = json.load(f)

        error_node_ids = {node['id'] for node in error_nodes}
        subgraph = {"nodes": [], "edges": []}

        # Filter nodes
        for node in main_graph['nodes']:
            if node['id'] in error_node_ids:
                subgraph['nodes'].append(node)

        # Filter edges
        for edge in main_graph['edges']:
            if edge['source'] in error_node_ids or edge['target'] in error_node_ids:
                subgraph['edges'].append(edge)

        # Write subgraph to file
        with open(subgraph_filename, "w") as f:
            json.dump(subgraph, f, indent=4)

        return subgraph
    except FileNotFoundError as e:
        print(f"Command failed with error: {e}")
        return {"Error" : f"Command failed with error: {e}"}
    except OSError as e:
        print(f"Command failed with error: {e}")
        return {"Error" : f"Command failed with error: {e}"}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"Error" : f"Command failed with error: {e}"}
    except:
        print(f"An error occurred.")
        return {"Error" : f"An error occurred."}

def create_subgraph_by_namespace(main_graph_filename: str, subgraph_filename: str, namespace: str) -> dict:
    """
    Create a subgraph from the main graph based on a specific namespace.

    Args:
        main_graph_filename (str): The name of the file containing the main graph data.
        subgraph_filename (str): The name of the file to write the subgraph data.
        namespace (str): The namespace to filter by.

    Returns:
        dict
    """

    try:
        with open(main_graph_filename, "r") as f:
            main_graph = json.load(f)

        subgraph = {"nodes": [], "edges": []}

        # Filter nodes by namespace
        namespace_node_ids = set()
        for node in main_graph['nodes']:
            if node.get('namespace') == namespace:
                subgraph['nodes'].append(node)
                namespace_node_ids.add(node['id'])

        # Filter edges that connect the filtered nodes
        for edge in main_graph['edges']:
            if edge['source'] in namespace_node_ids or edge['target'] in namespace_node_ids:
                subgraph['edges'].append(edge)

        # Write subgraph to file
        with open(subgraph_filename, "w") as f:
            json.dump(subgraph, f, indent=4)
        return subgraph
    except FileNotFoundError as e:
        print(f"Command failed with error: {e}")
        return {"Error" : f"Command failed with error: {e}"}
    except OSError as e:
        print(f"Command failed with error: {e}")
        return {"Error" : f"Command failed with error: {e}"}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"Error" : f"An error occurred: {e}"}
    except:
        print(f"An error occurred.")
        return {"Error" : f"An error occurred"}

def create_pod_subgraph(main_graph_filename: str, subgraph_filename: str, namespace: str, pod_name: str) -> dict:
    """
    Create a subgraph from the main graph based on a specific namespace and pod name.

    Args:
        main_graph_filename (str): The name of the file containing the main graph data.
        subgraph_filename (str): The name of the file to write the subgraph data.
        namespace (str): The namespace to filter by.
        pod_name (str): The name of the pod to filter by.

    Returns:
        dict
    """

    try:
        with open(main_graph_filename, "r") as f:
            main_graph = json.load(f)

        subgraph = {"nodes": [], "edges": []}

        # Filter nodes by namespace and pod name
        pod_node_id = None
        for node in main_graph['nodes']:
            if node.get('namespace') == namespace and node.get('name') == pod_name and node.get('kind') == "Pod":
                subgraph['nodes'].append(node)
                pod_node_id = node['id']
                break

        if pod_node_id is None:
            print(f"No pod found with name '{pod_name}' in namespace '{namespace}'")
            return

        # Filter edges that connect the filtered node
        for edge in main_graph['edges']:
            if edge['source'] == pod_node_id or edge['target'] == pod_node_id:
                subgraph['edges'].append(edge)

        # Write subgraph to file
        with open(subgraph_filename, "w") as f:
            json.dump(subgraph, f, indent=4)

        return subgraph
    except FileNotFoundError as e:
        print(f"Command failed with error: {e}")
        return {"Error" : f"Command failed with error: {e}"}
    except OSError as e:
        print(f"Command failed with error: {e}")
        return {"Error" : f"Command failed with error: {e}"}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"Error" : f"Command failed with error: {e}"}
    except:
        print(f"An error occurred.")
        return {"Error" : f"Command failed with error: {e}"}

def main():
    create_super_graph() # Create the super graph
    error_nodes = identify_error_prone_nodes(SUPER_GRAPH_PATH) # Identify error-prone nodes
    # print(json.dumps(error_nodes, indent=4)) # Print the error-prone nodes
    create_subgraph(SUPER_GRAPH_PATH, SUBGRAPH_PATH, error_nodes) # Create a subgraph based on error-prone nodes
    create_subgraph_by_namespace(SUPER_GRAPH_PATH, SUBGRAPH_NAMESPACES_PATH, "kube-system") # Create a subgraph based on a specific namespace
    create_pod_subgraph(SUPER_GRAPH_PATH, SUBGRAPH_POD_PATH, "kube-system", "coredns-7db6d8ff4d-hghgp") # Create a subgraph based on a specific pod



if __name__ == "__main__":
    main()