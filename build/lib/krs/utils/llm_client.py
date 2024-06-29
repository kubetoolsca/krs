import pickle
import subprocess
import os, time
from krs.utils.constants import (MAX_OUTPUT_TOKENS, LLMSTATE_PICKLE_FILEPATH)

class KrsGPTClient:

    def __init__(self, reinitialize=False, reset_history=False, device='cpu'):

        self.reinitialize = reinitialize
        self.client = None
        self.pipeline = None
        self.provider = None
        self.model = None
        self.openai_api_key = None
        self.continue_chat = False
        self.history = []
        self.max_tokens = MAX_OUTPUT_TOKENS
        self.device = device


        if not self.reinitialize:
            print("\nLoading LLM State..")
            self.load_state()
            print("\nModel: ", self.model)
        if not self.model:
            self.initialize_client()

        self.history = [] if reset_history == True else self.history

        if self.history:
            continue_chat = input("\n\nDo you want to continue previous chat ? (y/n) >> ")
            while continue_chat not in ['y', 'n']:
                print("Please enter either y or n!")
                continue_chat = input("\nDo you want to continue previous chat ? (y/n) >> ")
            if continue_chat == 'No':
                self.history = []
            else:
                self.continue_chat = True

    def save_state(self, filename=LLMSTATE_PICKLE_FILEPATH):
        state = {
            'provider': self.provider,
            'model': self.model,
            'history': self.history,
            'openai_api_key': self.openai_api_key
        }
        with open(filename, 'wb') as output:
            pickle.dump(state, output, pickle.HIGHEST_PROTOCOL)

    def load_state(self):
        try:
            with open(LLMSTATE_PICKLE_FILEPATH, 'rb') as f:
                state = pickle.load(f)
                self.provider = state['provider']
                self.model = state['model']
                self.history = state.get('history', [])
                self.openai_api_key = state.get('openai_api_key', '')
                if self.provider == 'OpenAI':
                    self.init_openai_client(reinitialize=True)
                elif self.provider == 'huggingface':
                    self.init_huggingface_client(reinitialize=True)
        except (FileNotFoundError, EOFError):
            pass

    def install_package(self, package_name):
        import importlib
        try:
            importlib.import_module(package_name)
            print(f"\n{package_name} is already installed.")
        except ImportError:
            print(f"\nInstalling {package_name}...", end='', flush=True)
            result = subprocess.run(['pip', 'install', package_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                print(f" \n{package_name} installed successfully.")
            else:
                print(f" \nFailed to install {package_name}.")


    def initialize_client(self):
        if not self.client and not self.pipeline:
            choice = input("\nChoose the model provider for healthcheck: \n\n[1] OpenAI \n[2] Huggingface\n\n>> ")
            if choice == '1':
                self.init_openai_client()
            elif choice == '2':
                self.init_huggingface_client()
            else:
                raise ValueError("Invalid option selected")

    def init_openai_client(self, reinitialize=False):

        if not reinitialize:
            print("\nInstalling necessary libraries..........")
            self.install_package('openai')
        
        import openai
        from openai import OpenAI

        self.provider = 'OpenAI'
        self.openai_api_key = input("\nEnter your OpenAI API key: ") if not reinitialize else self.openai_api_key
        self.model = input("\nEnter the OpenAI model name: ") if not reinitialize else self.model

        self.client = OpenAI(api_key=self.openai_api_key)

        if not reinitialize or self.reinitialize:
            while True:
                try:
                    self.validate_openai_key()
                    break
                except openai.error.AuthenticationError:
                    self.openai_api_key = input("\nInvalid Key! Please enter the correct OpenAI API key: ")
                except openai.error.InvalidRequestError as e:
                    print(e)
                    self.model = input("\nEnter an OpenAI model name from latest OpenAI docs: ")
                except openai.APIConnectionError as e:
                    print(e)
                    self.init_openai_client(reinitialize=False)

        self.save_state()

    def init_huggingface_client(self, reinitialize=False):

        if not reinitialize:
            print("\nInstalling necessary libraries..........")
            self.install_package('transformers')
            self.install_package('torch')
        
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

        import warnings
        from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer

        warnings.filterwarnings("ignore", category=FutureWarning)

        self.provider = 'huggingface'
        self.model = input("\nEnter the Huggingface model name: ") if not reinitialize else self.model

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model)
            self.model_hf = AutoModelForCausalLM.from_pretrained(self.model)
            self.pipeline = pipeline('text-generation', model=self.model_hf, tokenizer=self.tokenizer, device=0 if self.device == 'gpu' else -1)

        except OSError as e:
            print("\nError loading model: ", e)
            print("\nPlease enter a valid Huggingface model name.")
            self.init_huggingface_client(reinitialize=True)

        self.save_state()

    def validate_openai_key(self):
        """Validate the OpenAI API key by attempting a small request."""
        response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": "Test prompt, do nothing"}],
                    max_tokens=5
                )
        print("API key and model are valid.")

    def infer(self, prompt):
        self.history.append({"role": "user", "content": prompt})
        input_prompt = self.history_to_prompt()

        if self.provider == 'OpenAI':
            response = self.client.chat.completions.create(
                model=self.model,
                messages=input_prompt,
                max_tokens = self.max_tokens
            )
            output = response.choices[0].message.content.strip()

        elif self.provider == 'huggingface':
            responses = self.pipeline(input_prompt, max_new_tokens=self.max_tokens)
            output = responses[0]['generated_text']

        self.history.append({"role": "assistant", "content": output})
        print(">> ", output)

    def interactive_session(self, prompt_input):
        print("\nInteractive session started. Type 'end chat' to exit from the session!\n")

        if self.continue_chat:
            print('>> ', self.history[-1]['content'])
        else:
            initial_prompt = prompt_input
            self.infer(initial_prompt)

        while True:
            prompt = input("\n>> ")
            if prompt.lower() == 'end chat':
                break
            self.infer(prompt)
        self.save_state()

    def history_to_prompt(self):
        if self.provider == 'OpenAI':
            return self.history
        elif self.provider == 'huggingface':
            return " ".join([item["content"] for item in self.history])

if __name__ == "__main__":
    client = KrsGPTClient(reinitialize=False)
    # client.interactive_session("You are an 8th grade math tutor. Ask questions to gauge my expertise so that you can generate a training plan for me.")

