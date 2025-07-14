#!/usr/bin/env python3
"""
Setup script for Dark Pattern Annotation Interface
Helps create a virtual environment and install dependencies.
"""

import os
import sys
import subprocess
import venv
from pathlib import Path

def create_virtual_environment():
    """Create a virtual environment for the annotation interface."""
    venv_path = Path("annotation_env")
    
    if venv_path.exists():
        print(f"Virtual environment already exists at {venv_path}")
        return True
    
    print("Creating virtual environment...")
    try:
        venv.create(venv_path, with_pip=True)
        print(f"Virtual environment created at {venv_path}")
        return True
    except Exception as e:
        print(f"Error creating virtual environment: {e}")
        return False

def get_python_executable():
    """Get the Python executable path for the virtual environment."""
    if os.name == 'nt':  # Windows
        return "annotation_env\\Scripts\\python.exe"
    else:  # Unix/Linux/Mac
        return "annotation_env/bin/python"

def get_pip_executable():
    """Get the pip executable path for the virtual environment."""
    if os.name == 'nt':  # Windows
        return "annotation_env\\Scripts\\pip.exe"
    else:  # Unix/Linux/Mac
        return "annotation_env/bin/pip"

def install_dependencies():
    """Install required dependencies."""
    pip_exe = get_pip_executable()
    
    if not os.path.exists(pip_exe):
        print(f"Pip not found at {pip_exe}")
        return False
    
    print("Installing dependencies...")
    try:
        subprocess.run([pip_exe, "install", "flask==2.3.3", "flask-cors==4.0.0"], 
                      check=True, capture_output=True, text=True)
        print("Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False

def create_startup_script():
    """Create a startup script for the annotation server."""
    if os.name == 'nt':  # Windows
        script_content = '''@echo off
echo Dark Pattern Annotation Interface
echo =================================
echo.
echo Starting server...
echo.
echo The interface will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
python annotation_server.py
pause
'''
        script_path = "start_annotation_server.bat"
    else:  # Unix/Linux/Mac
        script_content = '''#!/bin/bash
echo "Dark Pattern Annotation Interface"
echo "================================"
echo ""
echo "Starting server..."
echo ""
echo "The interface will be available at: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""
python annotation_server.py
'''
        script_path = "start_annotation_server.sh"
        # Make executable
        os.chmod(script_path, 0o755)
    
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    print(f"Startup script created: {script_path}")

def main():
    print("Dark Pattern Annotation Interface Setup")
    print("=" * 40)
    print()
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"Python version: {sys.version}")
    print()
    
    # Create virtual environment
    if not create_virtual_environment():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Create startup script
    create_startup_script()
    
    print()
    print("Setup completed successfully!")
    print()
    print("To start the annotation interface:")
    print("1. Run the startup script: start_annotation_server.bat (Windows) or ./start_annotation_server.sh (Unix)")
    print("2. Or manually run: python annotation_server.py")
    print("3. Open your browser and go to: http://localhost:5000")
    print()
    print("For the standalone version (no server required):")
    print("1. Open simple_annotation_interface.html in your browser")
    print("2. This version works without Python dependencies")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 