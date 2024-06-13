#!/usr/bin/env python3

import typer, os
from krs.main import KrsMain
from krs.utils.constants import KRSSTATE_PICKLE_FILEPATH, KRS_DATA_DIRECTORY

app = typer.Typer() # Main typer app
krs = KrsMain() # Main class object


def check_initialized() -> None:
    
    """
    Checks if KRS is initialized or not.
    """
    try:
        if not os.path.exists(KRSSTATE_PICKLE_FILEPATH):
            typer.echo("KRS is not initialized. Please run 'krs init' first.")
            raise typer.Exit()
    except KeyboardInterrupt:
        typer.echo("\nExiting...")
        raise typer.Abort()
    except typer.Exit:
        raise typer.Abort()
    except typer.Abort:
        raise typer.Abort()
    except FileNotFoundError as e:
        typer.echo("Error: ", e)
        raise typer.Abort()
    except Exception as e:
        typer.echo("Error: ", e)
        raise typer.Abort()
    except:
        typer.echo("An error occured. Please try again.")
        raise typer.Abort()

try:
    if not os.path.exists(KRS_DATA_DIRECTORY): # Create data directory if not exists
        os.mkdir(KRS_DATA_DIRECTORY)
except KeyboardInterrupt as e:
    typer.echo("\nInterruption: ", e)
    raise typer.Abort()
except typer.Exit as e:
    typer.echo("\nExiting: ", e)
    raise typer.Abort()
except typer.Abort as e:
    typer.echo("\nAborting: ", e)
    raise typer.Abort()
except FileNotFoundError as e:
    typer.echo("Error: ", e)
    raise typer.Abort()
except Exception as e:
    typer.echo("Error: ", e)
    raise typer.Abort()
except:
    typer.echo("An error occured. Please try again.")
    raise typer.Abort()


@app.command() # Command to initialize the services
def init() -> None: # Function to initialize the services
    """
    Initializes the services and loads the scanner.
    """
    try:
        krs.initialize()
        typer.echo("Services initialized and scanner loaded.")
    except KeyboardInterrupt as e:
        typer.echo("\nInterruption: ", e)
        raise typer.Abort()
    except typer.Exit as e:
        typer.echo("\nExiting: ", e)
        raise typer.Abort()
    except typer.Abort as e:
        typer.echo("\nAborting: ", e)
        raise typer.Abort()
    except ValueError as e:
        typer.echo("Error: " + str(e))
        raise typer.Abort()
    except Exception as e:
        typer.echo("Error: ", e)
        raise typer.Abort()
    except:
        typer.echo("An error occured. Please try again.")
        raise typer.Abort()

# Command to scan the cluster
@app.command()
def scan() -> None:
    """
    Scans the cluster and extracts a list of tools that are currently used.
    """
    try:
        check_initialized()
        krs.scan_cluster()
    except KeyboardInterrupt as e:
        typer.echo("\nInterruption: ", e)
        raise typer.Abort()
    except typer.Exit as e:
        typer.echo("\nExiting: ", e)
        raise typer.Abort()
    except typer.Abort as e:
        typer.echo("\nAborting: ", e)
        raise typer.Abort()
    except Exception as e:
        typer.echo("Error: ", e)
        raise typer.Abort()
    except:
        typer.echo("An error occured. Please try again.")
        raise typer.Abort()

# Command to list all the namespaces
@app.command()
def namespaces() -> None:
    """
    Lists all the namespaces.
    """
    
    try:
        check_initialized()
        namespaces = krs.list_namespaces()
        typer.echo("Namespaces in your cluster are: \n")
        for i, namespace in enumerate(namespaces):
            typer.echo(str(i+1)+ ". "+ namespace)
    except KeyboardInterrupt as e:
        typer.echo("\nInterruption: ", e)
        raise typer.Abort()
    except typer.Exit as e:
        typer.echo("\nExiting: ", e)
        raise typer.Abort()
    except typer.Abort as e:
        typer.echo("\nAborting: ", e)
        raise typer.Abort()
    except Exception as e:
        typer.echo("Error: ", e)
        raise typer.Abort()
    except:
        typer.echo("An error occured. Please try again.")
        raise typer.Abort()

# Command to list all the pods
@app.command()
def pods(namespace: str = typer.Option(None, help="Specify namespace to list pods from")) -> None:
    
    """
    Lists all the pods with namespaces, or lists pods under a specified namespace.
    
    Args:
        namespace: str: Namespace name to list pods from.
    Returns:
        None
    """
    try:
        check_initialized()
        if namespace:
            pods = krs.list_pods(namespace)
            if pods == 'wrong namespace name':
                typer.echo(f"\nWrong namespace name entered, try again!\n")
                raise typer.Abort()
            typer.echo(f"\nPods in namespace '{namespace}': \n")
        else:
            pods = krs.list_pods_all()
            typer.echo("\nAll pods in the cluster: \n")
        
        for i, pod in enumerate(pods):
            typer.echo(str(i+1)+ '. '+ pod)
    except KeyboardInterrupt as e:
        typer.echo("\nInterruption: ", e)
        raise typer.Abort()
    except typer.Exit as e:
        typer.echo("\nExiting: ", e)
        raise typer.Abort()
    except typer.Abort as e:
        typer.echo("\nAborting: ", e)
        raise typer.Abort()
    except Exception as e:
        typer.echo("Error: ", e)
        raise typer.Abort()
    except:
        typer.echo("An error occured. Please try again.")
        raise typer.Abort()


@app.command()
def recommend(): # Command to recommend tools
    """
    Generates a table of recommended tools from our ranking database and their CNCF project status.
    """
    check_initialized()
    krs.generate_recommendations()

@app.command()
def health(change_model: bool = typer.Option(False, help="Option to reinitialize/change the LLM, if set to True")):
    """
    Starts an interactive terminal to chat with user.
    """
    check_initialized()
    typer.echo("\nStarting interactive terminal...\n")
    krs.health_check(change_model)

@app.command()
def export():
    """
    Exports pod info with logs and events.
    """
    check_initialized()
    krs.export_pod_info()
    typer.echo("Pod info with logs and events exported. Json file saved to current directory!")

@app.command()
def exit():
    """
    Ends krs services safely and deletes all state files from system. Removes all cached data.
    """
    check_initialized()
    krs.exit()
    typer.echo("Krs services closed safely.")

if __name__ == "__main__":
    app()
