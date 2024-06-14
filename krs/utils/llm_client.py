import pickle
import subprocess
import os, time
from krs.utils.constants import (MAX_OUTPUT_TOKENS, LLMSTATE_PICKLE_FILEPATH)

from krs.utils.log_manager import krs_logger


logger, log_with_exception = krs_logger()

# This class is used to interact with the OpenAI API or Huggingface API to generate responses for the given prompts.
class KrsGPTClient:

    # The constructor initializes the client and pipeline objects, and loads the state from the pickle file.
    
    def __init__(self, reinitialize : bool = False, reset_history : bool = False) -> None:


        """
        
        Initializes the KrsGPTClient object.
        
        Args:
            reinitialize (bool): Flag to indicate whether to reinitialize the client.
            reset_history (bool): Flag to indicate whether to reset the chat history.
        Returns:
            None
        
        """
        
        try:
            self.reinitialize = reinitialize
            self.client = None
            self.pipeline = None
            self.provider = None
            self.model = None
            self.openai_api_key = None
            self.continue_chat = False
            self.history = []
            self.max_tokens = MAX_OUTPUT_TOKENS
        
        except ValueError as e:
            log_with_exception(f"An error occurred during initialization: {e}", exc_info=True)
            raise
        except TypeError as e:
            log_with_exception(f"An error occurred during initialization: {e}", exc_info=True)
            raise
        except AttributeError as e:
            log_with_exception(f"An error occurred during initialization: {e}", exc_info=True)
            raise
        except KeyError as e:
            log_with_exception(f"An error occurred during initialization: {e}", exc_info=True)
            raise     
        except Exception as e:
            log_with_exception(f"An error occurred during initialization: {e}", exc_info=True)
            raise
        except:
            log_with_exception("An error occurred during initialization.")
            raise


        try:
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
        except ValueError as e:
            log_with_exception(f"An error occurred during initialization: {e}", exc_info=True)
            raise
        except TypeError as e:
            log_with_exception(f"An error occurred during initialization: {e}", exc_info=True)
            raise
        except AttributeError as e:
            log_with_exception(f"An error occurred during initialization: {e}", exc_info=True)
            raise
        except KeyError as e:
            log_with_exception(f"An error occurred during initialization: {e}", exc_info=True)
            raise
        except Exception as e:
            log_with_exception(f"An error occurred during initialization: {e}", exc_info=True)
            raise
        except:
            log_with_exception("An error occurred during initialization.", exc_info=True)
            raise

    def save_state(self, filename: str = LLMSTATE_PICKLE_FILEPATH) -> None:
        
        """
           save_state saves the state of the client to a pickle file.
           
           Args:
                filename (str): The path to the pickle file.
           Returns:
                None 
        """
        
        try:
            state = {
                'provider': self.provider,
                'model': self.model,
                'history': self.history,
                'openai_api_key': self.openai_api_key
            }
            with open(filename, 'wb') as output:
                pickle.dump(state, output, pickle.HIGHEST_PROTOCOL) # Save the state to a pickle file
        except FileNotFoundError as e:
            log_with_exception(f"Error: {e}", exc_info=True)
            raise
        except pickle.PickleError as e:
            log_with_exception(f"Error: {e}", exc_info=True)
            raise
        except Exception as e:
            log_with_exception(f"Error: {e}", exc_info=True)
            raise
        except:
            log_with_exception("An error occurred while saving the state.", exc_info=True)
            raise


    def load_state(self) -> None:
        
        """
        load_state loads the state of the client from a pickle file.
        
        Args:
            None
        Returns:
            None
        """
        
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
        except (FileNotFoundError, EOFError) as e:
            log_with_exception(f"No previous state found {e}", exc_info=True)
        except pickle.UnpicklingError as e:
            log_with_exception(f"Error loading state: {e}", exc_info=True)
            raise
        except pickle.PicklingError as e:
            log_with_exception(f"Error loading state: {e}", exc_info=True)
            raise
        except pickle.PickleError as e:
            log_with_exception(f"Error loading state: {e}", exc_info=True)
            raise
        except Exception as e:
            log_with_exception(f"Error loading state: {e}", exc_info=True)
            raise
        except:
            log_with_exception("An error occurred while loading the state ", exc_info=True)
            raise

    def install_package(self, package_name: str) -> None:
        
        """
        
        install_package installs the required package using pip.
        
        Args:
            package_name (str): The name of the package to install.
            
        Returns:
            None
            
        """
        
        import importlib
        try:
            importlib.import_module(package_name)
            print(f"\n{package_name} is already installed.")
        except ImportError:
            try:
                print(f"\nInstalling {package_name}...", end='', flush=True)
                result = subprocess.run(['pip', 'install', package_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE) # Install the package using pip
                if result.returncode == 0:
                    print(f" \n{package_name} installed successfully.")
                else:
                    print(f" \nFailed to install {package_name}.")
            except subprocess.CalledProcessError as e:
                log_with_exception(f"An error occurred while installing the package: {e}", exc_info=True)
                raise
            except subprocess.SubprocessError as e:
                log_with_exception(f"An error occurred while installing the package: {e}", exc_info=True)
                raise
            except Exception as e:
                log_with_exception(f"An error occurred while installing the package: {e}", exc_info=True)
                raise
            except:
                log_with_exception("An error occurred while installing the package.", exc_info=True)
                raise
        except Exception as e:
            log_with_exception(f"An error occurred while installing the package: {e}", exc_info=True)
            raise
        except:
            log_with_exception("An error occurred while installing the package.", exc_info=True)
            raise


    def initialize_client(self) -> None:
        
        """
        
        initialize_client initializes the client based on the user's choice of model provider.
        
        Args:
            None
        Returns:
            None
        """
        
        try:
            if not self.client and not self.pipeline:
                choice = input("\nChoose the model provider for healthcheck: \n\n[1] OpenAI \n[2] Huggingface\n\n>> ")
                if choice == '1':
                    self.init_openai_client()
                elif choice == '2':
                    self.init_huggingface_client()
                else:
                    raise ValueError("Invalid option selected")
        except ValueError as e:
            log_with_exception(f"An error occurred during initialization: {e}", exc_info=True)
            raise
        except TypeError as e:
            log_with_exception(f"An error occurred during initialization: {e}", exc_info=True)
            raise
        except AttributeError as e:
            log_with_exception(f"An error occurred during initialization: {e}", exc_info=True)
            raise
        except KeyError as e:
            log_with_exception(f"An error occurred during initialization: {e}", exc_info=True)
            raise
        except Exception as e:
            log_with_exception(f"An error occurred during initialization: {e}", exc_info=True)
            raise
        except:
            log_with_exception("An error occurred during initialization.", exc_info=True)
            raise

    def init_openai_client(self, reinitialize: bool = False) -> None:


        """
        
        init_openai_client initializes the OpenAI client.
        
        Args:
            reinitialize (bool): Flag to indicate whether to reinitialize the client.
            
        Returns:
            None
            
        """

        try:
            if not reinitialize:
                print("\nInstalling necessary libraries..........")
                self.install_package('openai')
        except ValueError as e:
            log_with_exception(f"An error occurred during initialization: {e}", exc_info=True)
            raise
        except TypeError as e:
            log_with_exception(f"An error occurred during initialization: {e}", exc_info=True)
            raise
        except AttributeError as e:
            log_with_exception(f"An error occurred during initialization: {e}", exc_info=True)
            raise
        except KeyError as e:
            log_with_exception(f"An error occurred during initialization: {e}", exc_info=True)
            raise
        except Exception as e:
            log_with_exception(f"An error occurred during initialization: {e}", exc_info=True)
            raise
        except:
            log_with_exception("An error occurred during initialization.", exc_info=True)
            raise
        
        try:
        
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
        except ValueError as e:
            log_with_exception(f"An error occurred during initialization: {e}", exc_info=True)
            raise
        except TypeError as e:
            log_with_exception(f"An error occurred during initialization: {e}", exc_info=True)
            raise
        except AttributeError as e:
            log_with_exception(f"An error occurred during initialization: {e}", exc_info=True)
            raise
        except KeyError as e:
            log_with_exception(f"An error occurred during initialization: {e}", exc_info=True)
            raise
        except Exception as e:
            log_with_exception(f"An error occurred during initialization: {e}", exc_info=True)
            raise
        except:
            print("An error occurred during initialization.", exc_info=True)
            raise

    def init_huggingface_client(self, reinitialize: bool = False) -> None:

        """
        
        init_huggingface_client initializes the Huggingface client.
        
        Args:
            reinitialize (bool): Flag to indicate whether to reinitialize the client.
            
        Returns:
            None
        
        """
        
        try:

            if not reinitialize:
                print("\nInstalling necessary libraries..........")
                self.install_package('transformers')
                self.install_package('torch')
                
        except ValueError as e:
            log_with_exception(f"An error occurred during initialization: {e}", exc_info=True)
            raise
        except TypeError as e:
            log_with_exception(f"An error occurred during initialization: {e}", exc_info=True)
            raise
        except AttributeError as e:
            log_with_exception(f"An error occurred during initialization: {e}", exc_info=True)
            raise
        except KeyError as e:
            log_with_exception(f"An error occurred during initialization: {e}", exc_info=True)
            raise
        except Exception as e:
            log_with_exception(f"An error occurred during initialization: {e}", exc_info=True)
            raise
        except:
            log_with_exception("An error occurred during initialization.", exc_info=True)
            raise
        
        try:
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # Suppress TensorFlow warnings

            import warnings
            from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer

            warnings.filterwarnings("ignore", category=FutureWarning) # Suppress FutureWarnings

            self.provider = 'huggingface'
            self.model = input("\nEnter the Huggingface model name: ") if not reinitialize else self.model

            try:
                self.tokenizer = AutoTokenizer.from_pretrained(self.model) # Load the tokenizer
                self.model_hf = AutoModelForCausalLM.from_pretrained(self.model) # Load the model
                self.pipeline = pipeline('text-generation', model=self.model_hf, tokenizer=self.tokenizer) # Create a pipeline

            except OSError as e:
                print("\nError loading model: ", e)
                print("\nPlease enter a valid Huggingface model name.")
                self.init_huggingface_client(reinitialize=True)

            self.save_state()
        except ValueError as e:
            log_with_exception(f"An error occurred during initialization: {e}", exc_info=True)
            raise
        except TypeError as e:
            log_with_exception(f"An error occurred during initialization: {e}", exc_info=True)
            raise
        except AttributeError as e:
            log_with_exception(f"An error occurred during initialization: {e}", exc_info=True)
            raise
        except KeyError as e:
            log_with_exception(f"An error occurred during initialization: {e}", exc_info=True)
            raise
        except Exception as e:
            log_with_exception(f"An error occurred during initialization: {e}", exc_info=True)
            raise
        except:
            log_with_exception("An error occurred during initialization.", exc_info=True)
            raise


    
    def validate_openai_key(self) -> None:
        
        """
        Validate the OpenAI API key by attempting a small request.
        
        Args:
            None
        Returns:
            None
            
        """
        
        try:
            
            # Test the API key by sending a small request
            response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[{"role": "user", "content": "Test prompt, do nothing"}],
                        max_tokens=5
                    )
            print("API key and model are valid.")
        # except openai.error.InvalidRequestError as e:
        #     log_with_exception(f"Error: {e}")
        #     raise
        # except openai.error.AuthenticationError as e:
        #     log_with_exception(f"Error: {e}")
        #     raise
        # except openai.APIConnectionError as e:
        #     log_with_exception(f"Error: {e}")
        #     raise
        except Exception as e:
            log_with_exception(f"Error: {e}", exc_info=True)
            raise


    def infer(self, prompt: str) -> None:
        
        """
        infer generates a response for the given prompt.
        
        Args:
            prompt (str): The user prompt.
            
        Returns:
            None
        """
        
        try:
            self.history.append({"role": "user", "content": prompt})
            input_prompt = self.history_to_prompt()

            if self.provider == 'OpenAI':
                response = self.client.chat.completions.create( # Generate a response
                    model=self.model,
                    messages=input_prompt,
                    max_tokens = self.max_tokens
                )
                output = response.choices[0].message.content.strip()

            elif self.provider == 'huggingface':
                responses = self.pipeline(input_prompt, max_new_tokens=self.max_tokens) # Generate a response
                output = responses[0]['generated_text']

            self.history.append({"role": "assistant", "content": output})
            print(">> ", output)
        except ValueError as e:
            log_with_exception(f"An error occurred during inference: {e}", exc_info=True)
            raise
        except TypeError as e:
            log_with_exception(f"An error occurred during inference: {e}", exc_info=True)
            raise
        except AttributeError as e:
            log_with_exception(f"An error occurred during inference: {e}", exc_info=True)
            raise
        except KeyError as e:
            log_with_exception(f"An error occurred during inference: {e}", exc_info=True)
            raise
        except Exception as e:
            log_with_exception(f"An error occurred during inference: {e}", exc_info=True)
            raise
        except:
            print("An error occurred during inference.", exc_info=True)
            raise

    def interactive_session(self, prompt_input: str) -> None:
        
        """
        interactive_session starts an interactive session with the user.
        
        Args:
            prompt_input (str): The initial prompt to start the conversation.
        Returns:
            None
        
        """
        
        try:
            
            print("\nInteractive session started. Type 'end chat' to exit from the session!\n")

            if self.continue_chat:
                print('>> ', self.history[-1]['content'])
            else:
                initial_prompt = prompt_input
                self.infer(initial_prompt) # Generate a response for the initial prompt

            while True:
                prompt = input("\n>> ")
                if prompt.lower() == 'end chat':
                    break
                self.infer(prompt)
            self.save_state()
            
        except ValueError as e:
            log_with_exception(f"An error occurred during the interactive session: {e}", exc_info=True)
            raise
        except TypeError as e:
            log_with_exception(f"An error occurred during the interactive session: {e}", exc_info=True)
            raise
        except AttributeError as e:
            log_with_exception(f"An error occurred during the interactive session: {e}", exc_info=True)
            raise
        except KeyError as e:
            log_with_exception(f"An error occurred during the interactive session: {e}", exc_info=True)
            raise
        except Exception as e:
            log_with_exception(f"An error occurred during the interactive session: {e}", exc_info=True)
            raise
        except:
            print("An error occurred during the interactive session.", exc_info=True)
            raise



    def history_to_prompt(self) -> list:
        
        """
        history_to_prompt converts the chat history to a prompt format.
        
        Args:
            None
        Returns:
            list: The chat history in prompt format.
        """
        
        try:
            if self.provider == 'OpenAI':
                return self.history
            elif self.provider == 'huggingface':
                return " ".join([item["content"] for item in self.history])
        except ValueError as e:
            log_with_exception(f"An error occurred during history conversion: {e}", exc_info=True)
            raise
        except TypeError as e:
            log_with_exception(f"An error occurred during history conversion: {e}", exc_info=True)
            raise
        except AttributeError as e:
            log_with_exception(f"An error occurred during history conversion: {e}", exc_info=True)
            raise
        except KeyError as e:
            log_with_exception(f"An error occurred during history conversion: {e}", exc_info=True)
            raise
        except Exception as e:
            log_with_exception(f"An error occurred during history conversion: {e}", exc_info=True)
            raise
        except:
            print("An error occurred during history conversion.", exc_info=True)
            raise

if __name__ == "__main__":
    client = KrsGPTClient(reinitialize=False) # Initialize the client
    # client.interactive_session("You are an 8th grade math tutor. Ask questions to gauge my expertise so that you can generate a training plan for me.")

