#!/usr/bin/env python3
"""
Development Environment Setup Script
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, description=None):
    """Run a shell command and print its output"""
    if description:
        print(f"\n{description}...")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error executing command: {command}")
        print(f"Error output: {result.stderr}")
        return False
    
    print(result.stdout)
    return True

def setup_virtual_environment():
    """Set up a virtual environment"""
    print("\nSetting up virtual environment...")
    
    # Check if venv already exists
    if os.path.exists("venv"):
        print("Virtual environment already exists. Skipping creation.")
        return True
    
    # Create virtual environment
    if not run_command("python -m venv venv", "Creating virtual environment"):
        return False
    
    print("Virtual environment created successfully.")
    return True

def install_dependencies():
    """Install project dependencies"""
    print("\nInstalling dependencies...")
    
    # Determine activate script based on platform
    if platform.system() == "Windows":
        activate_cmd = ".\\venv\\Scripts\\activate"
    else:
        activate_cmd = "source venv/bin/activate"
    
    # Install core dependencies
    if not run_command(f"{activate_cmd} && pip install -e .", "Installing package in development mode"):
        return False
    
    # Install development dependencies
    if not run_command(f"{activate_cmd} && pip install -r requirements-dev.txt", "Installing development dependencies"):
        return False
    
    print("Dependencies installed successfully.")
    return True

def setup_git_hooks():
    """Set up Git hooks using pre-commit"""
    print("\nSetting up Git hooks...")
    
    # Determine activate script based on platform
    if platform.system() == "Windows":
        activate_cmd = ".\\venv\\Scripts\\activate"
    else:
        activate_cmd = "source venv/bin/activate"
    
    # Install pre-commit
    if not run_command(f"{activate_cmd} && pip install pre-commit", "Installing pre-commit"):
        return False
    
    # Install git hooks
    if not run_command(f"{activate_cmd} && pre-commit install", "Installing Git hooks"):
        return False
    
    print("Git hooks set up successfully.")
    return True

def create_env_file():
    """Create .env file from .env.example if it doesn't exist"""
    print("\nSetting up environment variables...")
    
    # Check if .env already exists
    if os.path.exists(".env"):
        print(".env file already exists. Skipping creation.")
        return True
    
    # Check if .env.example exists
    if not os.path.exists(".env.example"):
        print("Warning: .env.example file not found. Cannot create .env file.")
        return False
    
    # Copy .env.example to .env
    try:
        with open(".env.example", "r") as example_file:
            with open(".env", "w") as env_file:
                env_file.write(example_file.read())
        print(".env file created successfully.")
        print("Please update .env with your actual configuration values.")
        return True
    except Exception as e:
        print(f"Error creating .env file: {e}")
        return False

def main():
    """Main function"""
    print("Setting up development environment for Adaptive MCP Server...")
    
    # Ensure we're in the project root directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir.parent)
    
    # Setup steps
    steps = [
        setup_virtual_environment,
        install_dependencies,
        setup_git_hooks,
        create_env_file,
    ]
    
    # Run all steps
    success = True
    for step in steps:
        if not step():
            success = False
            break
    
    if success:
        print("\nDevelopment environment setup complete!")
        print("\nTo activate the virtual environment:")
        if platform.system() == "Windows":
            print("    .\\venv\\Scripts\\activate")
        else:
            print("    source venv/bin/activate")
        print("\nTo run tests:")
        print("    pytest tests/test_simplified.py -v")
        return 0
    else:
        print("\nDevelopment environment setup failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
