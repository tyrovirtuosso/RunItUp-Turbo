#!/bin/bash

# Make script executable: `chmod +x run_script.sh`

# Define the full path to the virtual environment
VENV_PATH="/path/to/your/virtual/environment"

# Activate the virtual environment
source "$VENV_PATH/bin/activate"

# Modify PYTHONPATH and PATH to use absolute paths
export PYTHONPATH="/path/to/your/project:$PYTHONPATH"
export PATH="$PATH:$VENV_PATH/bin:/usr/sbin"

# Set the full path to a custom command as an environment variable
export PROTONVPN_CMD="/path/to/your/protonvpn"

# Change to the script directory using an absolute path
cd "/path/to/your/project"

# Execute the Python script
sudo -E "/path/to/your/virtual/environment/bin/python" -m your_module_name.main
