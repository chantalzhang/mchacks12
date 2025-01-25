#!/bin/bash

# Check if venv exists, if not create it
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Install/update requirements
echo "Installing requirements..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    VENV_PATH="./venv/Scripts"
else
    VENV_PATH="./venv/bin"
fi

"$VENV_PATH/pip" install -r requirements.txt || {
    echo "Error: Failed to install requirements"
    exit 1
}

