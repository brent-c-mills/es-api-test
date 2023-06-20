#!/bin/bash

# Check if Python 3.11 is installed
python_version=$(python3 --version 2>&1)
if [[ $python_version =~ Python\ 3\.11 ]]; then
    echo "Python 3.11 is already installed."
else
    read -p "Python 3.11 is required but not found. Do you want to install it? (Y/n) " install_python
    if [[ $install_python =~ ^[Yy]$ ]]; then
        # Install Python 3.11 on CentOS 8
        if [ -f /etc/redhat-release ]; then
            sudo dnf install -y python39
        fi
        
        # Install Python 3.11 on macOS 12
        if [[ $(uname) == "Darwin" ]]; then
            brew install python@3.9
        fi
    else
        echo "Dependency not met. Exiting."
        exit 1
    fi
fi

# Check if Pip is installed
pip_version=$(pip3 --version 2>&1)
if [[ ! $pip_version =~ "not found" ]]; then
    echo "Pip is already installed."
else
    read -p "Pip is required but not found. Do you want to install it? (Y/n) " install_pip
    if [[ $install_pip =~ ^[Yy]$ ]]; then
        # Install Pip
        python3 -m ensurepip --upgrade --default-pip
        
        # Add pip to PATH on macOS
        if [[ $(uname) == "Darwin" ]]; then
            echo "export PATH=$HOME/Library/Python/3.9/bin:$PATH" >> ~/.bash_profile
            source ~/.bash_profile
        fi
    else
        echo "Dependency not met. Exiting."
        exit 1
    fi
fi

# Install the remaining dependencies using Pip
echo "Installing dependencies..."
pip3 install -U uvicorn fastapi pydantic email-validator pyyaml

echo "Installation completed successfully."
