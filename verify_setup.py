#!/usr/bin/env python3
"""
verify_setup.py - Check if everything is installed correctly
Run this before building to make sure all dependencies are available.
"""

import sys
import subprocess
from pathlib import Path


def check_command(command, name, install_hint):
    """Check if a command is available"""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            shell=False
        )
        print("[OK] {0} is installed".format(name))
        return True
    except FileNotFoundError:
        print("[MISSING] {0} is NOT installed".format(name))
        print("   Install with: {0}".format(install_hint))
        return False


def check_file(filepath, description):
    """Check if a required file exists"""
    if Path(filepath).exists():
        print("[OK] {0} exists".format(description))
        return True
    else:
        print("[MISSING] {0} is MISSING".format(description))
        return False


def main():
    print("="*60)
    print("SETUP VERIFICATION")
    print("="*60)
    print()
    
    all_good = True
    
    # Check Python version
    print("Checking Python...")
    py_version = sys.version_info
    if py_version.major == 3 and py_version.minor >= 8:
        print("[OK] Python {0}.{1}.{2}".format(py_version.major, py_version.minor, py_version.micro))
    else:
        print("[WARNING] Python {0}.{1}.{2} (3.8+ recommended)".format(py_version.major, py_version.minor, py_version.micro))
    print()
    
    # Check Python packages
    print("Checking Python packages...")
    
    packages = {
        'mkdocs': 'pip install mkdocs',
        'material': 'pip install mkdocs-material',
        'yaml': 'pip install pyyaml'
    }
    
    for package, install_cmd in packages.items():
        try:
            __import__(package)
            print("[OK] {0} is installed".format(package))
        except ImportError:
            print("[MISSING] {0} is NOT installed".format(package))
            print("   Install with: {0}".format(install_cmd))
            all_good = False
    print()
    
    # Check Node.js and npm
    print("Checking Node.js tools...")
    node_ok = check_command(
        ["node", "--version"],
        "Node.js",
        "Download from https://nodejs.org"
    )
    
    npm_ok = check_command(
        ["npm", "--version"],
        "npm",
        "Comes with Node.js"
    )
    print()
    
    # Check StatiCrypt
    print("Checking encryption tools...")
    staticrypt_ok = check_command(
        ["staticrypt", "--version"],
        "StatiCrypt",
        "npm install -g staticrypt"
    )
    print()
    
    # Check required files
    print("Checking required files...")
    file_checks = [
        ("build_nav.py", "build_nav.py"),
        ("mkdocs.yml", "mkdocs.yml (base config)"),
        ("publish.py", "publish.py"),
        ("deploy_site.bat", "deploy_site.bat"),
        ("docs", "docs folder")
    ]
    
    for filepath, description in file_checks:
        if not check_file(filepath, description):
            all_good = False
    print()
    
    # Check virtual environment
    print("Checking virtual environment...")
    if Path("venv").exists() or Path("env").exists():
        print("[OK] Virtual environment folder exists")
        if sys.prefix != sys.base_prefix:
            print("[OK] Virtual environment is ACTIVATED")
        else:
            print("[WARNING] Virtual environment exists but is NOT activated")
            print("   Activate with: .\\venv\\Scripts\\activate")
    else:
        print("[WARNING] Virtual environment not found")
        print("   Create with: python -m venv venv")
    print()
    
    # Check git
    print("Checking version control...")
    check_command(
        ["git", "--version"],
        "Git",
        "Download from https://git-scm.com"
    )
    print()
    
    # Summary
    print("="*60)
    if all_good and staticrypt_ok:
        print("EVERYTHING LOOKS GOOD!")
        print("="*60)
        print("You're ready to build your site!")
        print()
        print("Next stepscls:")
        print("1. Make sure docs/index.md exists")
        print("2. Run: python publish.py")
        print("3. Deploy: deploy_site.bat")
    else:
        print("SOME ITEMS NEED ATTENTION")
        print("="*60)
        print("Please install missing dependencies and try again.")
        print()
        if not staticrypt_ok:
            print("[WARNING] Note: Without StatiCrypt, your site won't be encrypted!")


if __name__ == "__main__":
    main()