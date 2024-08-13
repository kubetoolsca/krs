# import requests
# import subprocess
# import shlex

import subprocess
import sys
import shlex
import os
import time
import json


required_packages = [
    "requests",
]

init_complete = 0
chat_history_file = "chat_history.json"
chat_history = []


def install_lib(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def install_packages(req_packages):

    for package in req_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"{package} not found. Installing...")
            install_lib(package)

try:
    import requests
except ImportError:
    install_packages(required_packages)
    import requests


def check_initialization_complete():

    global init_complete
    repo_path = os.path.join(os.getcwd(), "LocalAI")
    model_path = os.path.join(repo_path, "models", "luna-ai-llama2")
    tmpl_path = os.path.join(repo_path, "models", "luna-ai-llama2.tmpl")
    
    if os.path.isdir(repo_path) and os.path.isfile(model_path) and os.path.isfile(tmpl_path):
        print("Initialization is complete.")
        init_complete = 1
        return True
    else:
        print("Initialization is not complete.")
        return False

def init_setup():

    global init_complete
    init_complete = 1
    
    # os.chdir("..")
    run_command("git clone https://github.com/go-skynet/LocalAI")
    os.chdir("LocalAI")
    run_command("wget https://huggingface.co/TheBloke/Luna-AI-Llama2-Uncensored-GGUF/resolve/main/luna-ai-llama2-uncensored.Q4_0.gguf -O models/luna-ai-llama2")
    run_command("cp -rf prompt-templates/getting_started.tmpl models/luna-ai-llama2.tmpl")

def localai_start():
    if (check_docker() == True) and (init_complete == 1):
        if not check_containers_running():
            #if os.path.basename(os.getcwd()) != "LocalAI":
                #os.chdir("../LocalAI")
            os.chdir("LocalAI")
            run_command("docker compose up -d --pull always", retries=3, timeout=360)


def run_command(command_str, retries=3, timeout=120):
    global init_complete
    command_list = shlex.split(command_str)
    for attempt in range(retries):
        try:
            print(f"Running: {command_str} (Attempt {attempt + 1}/{retries})")
            result = subprocess.run(command_list, capture_output=True, check=True, timeout=timeout, text=True)
            print(f"Completed: {command_str}")
            init_complete = init_complete & 1
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            print(f"Timeout expired for: {command_str}")
            init_complete = init_complete & 0
        except subprocess.CalledProcessError as e:
            print(f"Command failed with error: {e}")
            init_complete = init_complete & 0
        time.sleep(5)  # Wait before retrying
    return False


def check_docker():
    output = run_command("docker --version")
    if output != True:
        print("You need to install docker to commmense with LocalAI")
        return False
    return True

def load_chat_history():
    global chat_history
    if os.path.exists(chat_history_file):
        with open(chat_history_file, "r") as file:
            chat_history = json.load(file)
            print("Chat history loaded.")

def save_chat_history():
    with open(chat_history_file, "w") as file:
        json.dump(chat_history, file)
        print("Chat history saved.")

def check_containers_running():
    try:
        result = subprocess.run(["docker", "ps"], capture_output=True, check=True, text=True)
        if "localai-api-1" in result.stdout: 
            print("Required containers are already running.")
            return True
        else:
            print("Required containers are not running.")
            return False
    except subprocess.CalledProcessError:
        print("Failed to check running containers.")
        return False

def handle_chat(chat_history):
    localai_start()
    while True:
        user_input = input("You: ")
        if user_input.lower() == "end chat":
            print("Ending chat. Goodbye!")
            break
        response = chat(user_input,chat_history)
        print(f"Assistant: {response['choices'][0]['message']['content']}")


def chat(chat_question,chat_history):


    url = "http://localhost:8080/v1/chat/completions"
    headers = {"Content-Type": "application/json"}

    chat_history.append({"role": "user", "content": chat_question})

    data = {
    "model": "luna-ai-llama2",
    #"messages": [{"role": "user", "content": chat_question}],
    "messages": chat_history,
    "temperature": 0.9
    }

    response = requests.post(url, headers=headers, json=data)
    response_data = response.json()

    chat_history.append({"role": "assistant", "content": response_data['choices'][0]['message']['content']})

    #save_chat_history()

    return response_data['choices'][0]['message']['content']


def total_initialization():
    global init_complete
    if not check_initialization_complete():
        init_setup()
    localai_start()


def main():
    global init_complete
    if not check_initialization_complete():
        init_setup()
    localai_start()
    load_chat_history()

    handle_chat(chat_history)

if __name__ == "__main__":
    main()