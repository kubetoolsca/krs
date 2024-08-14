# Author: Oluchukwu Obi-Njoku
# Date: 2024-08-13


""" 
Description: 

This script facilitates interaction with the LocalAI API. It includes functionality to:
1. Start and manage LocalAI Docker containers.
2. Handle chat interactions with the LocalAI API.
3. Initialize the LocalAI API if it has not been initialized yet.

The script ensures seamless communication with the LocalAI service, 
providing methods to send chat messages and receive responses, while also managing the 
lifecycle of the LocalAI Docker containers.

"""

#import required libraries

import subprocess
import sys
import shlex
import os
import time
import json



# Global variables

# Define required packages
required_packages = [
    "requests",
]

# Define global variable to track initialization status
init_complete = 0



def install_lib(package: str) -> None:

    """
    Install a Python package using pip
    
    Args: package (str): The name of the package to install
    Returns: None
    """
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package]) # Install the package
    except subprocess.CalledProcessError as e:
        print(f"Error installing package: {package}")
        print(e)
    except Exception as e:
        print(f"An error occurred: {e}")
    except:
        print(f"Failed to install {package}.")

def install_packages(req_packages: list) -> None:

    """
    Install required Python packages using pip

    Args: req_packages (list): A list of required package names
    Returns: None
    """

    for package in req_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"{package} not found. Installing...")
            install_lib(package)
        except Exception as e:
            print(f"An error occurred: {e}")
        except:
            print(f"Failed to install {package}.")


# Import required packages if they are installed
# If not, install the required packages
# Then import the packages

try:
    import requests
except ImportError:
    install_packages(required_packages) # Install required packages
    import requests


def check_initialization_complete()-> bool:

    """
    Check if the LocalAI API has been initialized

    Args: None
    Returns: bool: True if initialization is complete, False otherwise
    """

    try:
        # Define paths for model and template files
        global init_complete
        repo_path = os.path.join(os.getcwd(), "LocalAI")
        model_path = os.path.join(repo_path, "models", "luna-ai-llama2")
        tmpl_path = os.path.join(repo_path, "models", "luna-ai-llama2.tmpl")
        
        # Check if the required files and directories exist
        if os.path.isdir(repo_path) and os.path.isfile(model_path) and os.path.isfile(tmpl_path): # Check if the model and template files exist
            print("Initialization is complete.") # Initialization is complete
            init_complete = 1
            return True
        else:
            print("Initialization is not complete.") # Initialization is not complete
            return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    except:
        print("Failed to check initialization status.")
        return False


def init_setup() -> None:

    """
    Initialize the LocalAI API by cloning the repository and downloading the model and template files

    Args: None
    Returns: None
    """

    try:
        run_command("git clone https://github.com/go-skynet/LocalAI")
        os.chdir("LocalAI")
        run_command("wget https://huggingface.co/TheBloke/Luna-AI-Llama2-Uncensored-GGUF/resolve/main/luna-ai-llama2-uncensored.Q4_0.gguf -O models/luna-ai-llama2")
        run_command("cp -rf prompt-templates/getting_started.tmpl models/luna-ai-llama2.tmpl")
    except Exception as e:
        print(f"An error occurred: {e}")
    except:
        print("Failed to initialize LocalAI.")


def localai_start() -> None:

    """
    Start the LocalAI API Docker containers

    Args: None
    Returns: None
    """

    try:
        if (check_docker() == True) and (init_complete == 1):
            if not check_containers_running():
                if os.path.basename(os.getcwd()) != "LocalAI":
                    os.chdir("LocalAI")
                run_command("docker compose up -d --pull always", retries=3, timeout=360)
    except Exception as e:
        print(f"An error occurred: {e}")
    except:
        print("Failed to start LocalAI.")
        

def run_command(command_str: str, retries: int=3, timeout: int=120) -> bool:

    """
    Run a command in the shell and handle retries and timeouts

    Args:   command_str (str): The command to run
            retries (int): The number of times to retry the command
            timeout (int): The timeout for the command

    Returns: bool: True if the command was successful, False otherwise
    """

    global init_complete
    command_list = shlex.split(command_str) # Split the command string into a list

    # Retry the command multiple times
    for attempt in range(retries):
        try:

            print(f"Running: {command_str} (Attempt {attempt + 1}/{retries})")
            result = subprocess.run(command_list, capture_output=True, check=True, timeout=timeout, text=True) # Run the command
            print(f"Completed: {command_str}") # Print the command completion message
            init_complete = init_complete & 1 # Set initialization status to complete
            return result.returncode == 0 # Return True if the command was successful

        except subprocess.TimeoutExpired:
            print(f"Timeout expired for: {command_str}")
            init_complete = init_complete & 0
            return False

        except subprocess.CalledProcessError as e:
            print(f"Command failed with error: {e}")
            init_complete = init_complete & 0
            return False
        
        except Exception as e:
            print(f"An error occurred: {e}")
            init_complete = init_complete & 0
            return False
        
        except:
            print(f"Failed to run command: {command_str}")
            init_complete = init_complete & 0
            return False

        time.sleep(5)  # Wait before retrying
    return False


def check_docker() -> bool:

    """
    Check if Docker is installed on the system

    Args: None
    Returns: bool: True if Docker is installed, False otherwise
    """

    try:
        output = run_command("docker --version")
        if output != True:
            print("You need to install docker to commmense with LocalAI")
            return False
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    except:
        print("Failed to check Docker installation.")
        return False


def check_containers_running() -> bool:

    """
    Check if the required LocalAI Docker containers are running

    Args: None
    Returns: bool: True if the containers are running, False otherwise
    """

    try:
        result = subprocess.run(["docker", "ps"], capture_output=True, check=True, text=True) # Run the command to check running containers
        if "localai-api-1" in result.stdout:  # Check if the required containers are running
            print("Required containers are already running.")
            return True
        else:
            print("Required containers are not running.")
            return False
    except subprocess.CalledProcessError:
        print("Failed to check running containers.")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    except:
        print("Failed to check running containers.")
        return False

def handle_chat(chat_history: list) -> None:

    """
    Handle chat interactions with the LocalAI API

    Args: chat_history (list): A list of chat messages
    Returns: None
    """

    try:
        localai_start() # Start the LocalAI API
        while True:
            user_input = input("You: ")
            if user_input.lower() == "end chat":
                print("Ending chat. Goodbye!")
                break
            response = chat(chat_history) # Get a response from the LocalAI API
            print(f"Assistant: {response['choices'][0]['message']['content']}")
    except Exception as e:
        print(f"An error occurred: {e}")
    except:
        print("Failed to handle chat interactions.")


def chat(chat_history: list) -> str:

    """
    Send chat messages to the LocalAI API and receive responses

    Args: chat_history (list): A list of chat messages
    Returns: str: The response from the LocalAI API
    """

    localai_start() # Start the LocalAI API

    url = "http://localhost:8080/v1/chat/completions" # Define the API endpoint
    headers = {"Content-Type": "application/json"} # Define the request headers

    data = {
        "model": "luna-ai-llama2",
        "messages": chat_history,
        "temperature": 0.9
    } # Define the request data

    try:
        response = requests.post(url, headers=headers, json=data, timeout=360)  # Set timeout to 10 seconds
        response.raise_for_status()  # Raise an error for bad status codes
        response_data = response.json() # Get the response data
        return response_data['choices'][0]['message']['content']
    except requests.exceptions.Timeout:
        return "The request timed out"
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"
    except Exception as e:
        return f"An error occurred: {e}"
    except:
        return "Failed to send chat message."

def total_initialization() -> None:

    """
    Initialize the LocalAI API and start the LocalAI Docker containers

    Args: None
    Returns: None
    """
    try:
        global init_complete 
        if not check_initialization_complete(): # Check if the LocalAI API has been initialized
            init_setup() # Initialize the LocalAI API
        localai_start() # Start the LocalAI Docker containers
    except Exception as e:
        print(f"An error occurred: {e}")
    except:
        print("Failed to complete initialization.")

