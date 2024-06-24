#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Install the requirements
pip install -r krs/requirements.txt --extra-index-url https://download.pytorch.org/whl/cu121

# Run the Python script
python krs/printdependency.py
