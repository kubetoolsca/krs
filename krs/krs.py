#!/usr/bin/env python3

import typer
import os
import logging
from krs.main import KrsMain
from krs.utils.constants import KRSSTATE_PICKLE_FILEPATH, KRS_DATA_DIRECTORY

app = typer.Typer(help="krs: A command line interface to scan your Kubernetes Cluster, detect errors, provide resolutions using LLMs and recommend latest tools for your cluster")
krs = KrsMain()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_initialized():
    if not os.path.exists(KRSSTATE_PICKLE_FILEPATH):
        typer.echo("KRS is not initialized. Please run 'krs init' first.")
        raise typer.Exit()

if not os.path.exists(KRS_DATA_DIRECTORY):
    os.makedirs(KRS_DATA_DIRECTORY)

@app.command()
def init(kubeconfig: str = typer.Option('~/.kube/config', help="Custom path for kubeconfig file if not default")):
    """
    Initializes the services and loads the scanner.
    """
    try:
        krs.initialize(kubeconfig)
        typer.echo("Services initialized and scanner loaded.")
        logging.info("KRS initialized successfully with kubeconfig: %s", kubeconfig)
    except Exception as e:
        typer.echo(f"Failed to initialize KRS: {e}")
        logging.error("Failed to initialize KRS: %s", e)
        raise typer.Exit(code=1)

@app.command()
def scan():
    """
    Scans the cluster and extracts a list of tools that are currently used.
    """
    check_initialized()
    try:
        krs.scan_cluster()
        typer.echo("Cluster scanned successfully.")
        logging.info("Cluster scanned successfully.")
    except Exception as e:
        typer.echo(f"Failed to scan cluster: {e}")
        logging.error("Failed to scan cluster: %s", e)
        raise typer.Exit(code=1)

@app.command()
def namespaces():
    """
    Lists all the namespaces.
    """
    check_initialized()
    try:
        namespaces = krs.list_namespaces()
        typer.echo("Namespaces in your cluster are: \n")
        for i, namespace in enumerate(namespaces):
            typer.echo(str(i + 1) + ". " + namespace)
        logging.info("Listed namespaces successfully.")
    except Exception as e:
        typer.echo(f"Failed to list namespaces: {e}")
        logging.error("Failed to list namespaces: %s", e)
        raise typer.Exit(code=1)

@app.command()
def pods(namespace: str = typer.Option(None, help="Specify namespace to list pods from")):
    """
    Lists all the pods with namespaces, or lists pods under a specified namespace.
    """
    check_initialized()
    try:
        if namespace:
            pods = krs.list_pods(namespace)
            if pods == 'wrong namespace name':
                typer.echo(f"\nWrong namespace name entered, try again!\n")
                logging.warning("Wrong namespace name entered: %s", namespace)
                raise typer.Abort()
            typer.echo(f"\nPods in namespace '{namespace}': \n")
        else:
            pods = krs.list_pods_all()
            typer.echo("\nAll pods in the cluster: \n")

        for i, pod in enumerate(pods):
            typer.echo(str(i + 1) + '. ' + pod)
        logging.info("Listed pods successfully for namespace: %s", namespace if namespace else "all")
    except Exception as e:
        typer.echo(f"Failed to list pods: {e}")
        logging.error("Failed to list pods: %s", e)
        raise typer.Exit(code=1)

@app.command()
def recommend():
    """
    Generates a table of recommended tools from our ranking database and their CNCF project status.
    """
    check_initialized()
    try:
        krs.generate_recommendations()
        logging.info("Generated tool recommendations successfully.")
    except Exception as e:
        typer.echo(f"Failed to generate recommendations: {e}")
        logging.error("Failed to generate recommendations: %s", e)
        raise typer.Exit(code=1)


@app.command()
def health(change_model: bool = typer.Option(False, help="Option to reinitialize/change the LLM"),
           device: str = typer.Option('cpu', help='Option to run Huggingface models on GPU by entering the option as "gpu"')):
    """
    Starts an interactive terminal using an LLM of your choice to detect and fix issues with your cluster
    """
    check_initialized()
    typer.echo("\nStarting interactive terminal...\n")
    krs.health_check(change_model, device)

# @app.command()
# def health(change_model: bool = typer.Option(False, help="Option to reinitialize/change the LLM, if set to True"),
#            device: str = typer.Option('cpu', help='Option to run Huggingface models on GPU by entering the option as "gpu"')):
#     """
#     Starts an interactive terminal using an LLM of your choice to detect and fix issues with your cluster
#     """
#     check_initialized()
#     typer.echo("\nStarting interactive terminal...\n")
#     try:
#         krs.health_check(change_model, device)
#         logging.info("Started interactive terminal for health check with model change: %s, device: %s", change_model, device)
#     except Exception as e:
#         typer.echo(f"Failed to start interactive terminal: {e}")
#         logging.error("Failed to start interactive terminal: %s", e)
#         raise typer.Exit(code=1)

@app.command()
def export():
    """
    Exports pod info with logs and events.
    """
    check_initialized()
    try:
        krs.export_pod_info()
        typer.echo("Pod info with logs and events exported. JSON file saved to current directory!")
        logging.info("Pod info exported successfully.")
    except Exception as e:
        typer.echo(f"Failed to export pod info: {e}")
        logging.error("Failed to export pod info: %s", e)
        raise typer.Exit(code=1)

@app.command()
def clean():
    """
    Ends KRS services safely and deletes all state files from the system. Removes all cached data.
    """
    check_initialized()
    try:
        krs.exit()
        typer.echo("KRS services closed safely.")
        logging.info("KRS services closed and state files deleted successfully.")
    except Exception as e:
        typer.echo(f"Failed to close KRS services: {e}")
        logging.error("Failed to close KRS services: %s", e)
        raise typer.Exit(code=1)

@app.command()
def version():
    """
    Displays the current version of KRS.
    """
    try:
        # Assuming there's a VERSION file or a version attribute in KrsMain
        version = "1.0.0"  # Replace with actual version fetching logic
        typer.echo(f"KRS version: {version}")
        logging.info("Displayed KRS version: %s", version)
    except Exception as e:
        typer.echo(f"Failed to fetch version: {e}")
        logging.error("Failed to fetch version: %s", e)
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()

@app.command()
def version():
    """
    Displays the current version of KRS.
    """
    try:
        version = krs.get_version()
        typer.echo(f"KRS version: {version}")
        logging.info("Displayed KRS version: %s", version)
    except Exception as e:
        typer.echo(f"Failed to fetch version: {e}")
        logging.error("Failed to fetch version: %s", e)
        raise typer.Exit(code=1)
