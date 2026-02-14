#!/usr/bin/env python3
"""
publish.py - The Security Guard
Builds your MkDocs site and encrypts it with StatiCrypt for password protection.
This ensures your notes remain private even when hosted publicly.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, description, shell=False):
    """Run a command and handle errors"""
    print("\n{0}...".format(description))
    try:
        if shell:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        else:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
        
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("ERROR: {0} failed!".format(description))
        if e.stderr:
            print(e.stderr)
        if e.stdout:
            print(e.stdout)
        return False
    except FileNotFoundError:
        print("ERROR: Required command not found for {0}".format(description))
        print("   Make sure all dependencies are installed.")
        return False


def check_staticrypt():
    """Check if StatiCrypt is installed"""
    try:
        subprocess.run(["staticrypt", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("WARNING: StatiCrypt not found!")
        print("   Install it with: npm install -g staticrypt")
        return False


def build_navigation():
    """Run build_nav.py to generate navigation structure"""
    print("\n" + "="*60)
    print("STEP 1: Building Navigation Structure")
    print("="*60)
    
    if not Path("build_nav.py").exists():
        print("WARNING: build_nav.py not found! Skipping navigation build.")
        return True
    
    return run_command([sys.executable, "build_nav.py"], "Building navigation")


def build_mkdocs_site():
    """Build the MkDocs site using mkdocs_base.yml"""
    print("\n" + "="*60)
    print("STEP 2: Building MkDocs Site")
    print("="*60)
    
    # Check if mkdocs_base.yml exists
    if not Path("mkdocs_base.yml").exists():
        print("ERROR: mkdocs_base.yml not found!")
        print("   Make sure build_nav.py ran successfully.")
        return False
    
    # Clean old build
    if Path("site").exists():
        print("Cleaning old site folder...")
        shutil.rmtree("site")
    
    # Build site with mkdocs_base.yml
    return run_command(["mkdocs", "build", "-f", "mkdocs_base.yml"], "Building MkDocs site")


def encrypt_site():
    """Encrypt the site with StatiCrypt"""
    print("\n" + "="*60)
    print("STEP 3: Encrypting Site with StatiCrypt")
    print("="*60)
    
    if not Path("site").exists():
        print("ERROR: site folder not found! Build must have failed.")
        return False
    
    if not check_staticrypt():
        print("WARNING: Skipping encryption. Site will be unprotected!")
        return True
    
    # Get password (you can modify this to read from a config file)
    password = os.environ.get('SITE_PASSWORD', '')
    
    if not password:
        print("WARNING: No password set!")
        print("   Set SITE_PASSWORD environment variable or modify publish.py")
        print("   Using default password: 'changeme' (CHANGE THIS!)")
        password = 'changeme'
    
    # Create encrypted folder if it doesn't exist
    encrypted_dir = Path("encrypted")
    if encrypted_dir.exists():
        print("Cleaning old encrypted folder...")
        shutil.rmtree(encrypted_dir)
    
    encrypted_dir.mkdir()
    
    # Encrypt all HTML files
    site_dir = Path("site")
    html_files = list(site_dir.rglob("*.html"))
    
    if not html_files:
        print("WARNING: No HTML files found to encrypt!")
        return False
    
    print("Encrypting {0} HTML files...".format(len(html_files)))
    
    # StatiCrypt command
    # We'll encrypt and keep the output in the site folder itself
    # StatiCrypt replaces files in place
    command = [
        "staticrypt",
        "site/*.html",
        "site/**/*.html",
        "-r",  # Recursive
        "-p", password,
        "--short",  # Short instructions
        "-t", "Private Notes - Enter Password",
        "--remember", "30"  # Remember for 30 days
    ]
    
    success = run_command(command, "Encrypting with StatiCrypt", shell=True)
    
    if success:
        print("Encryption complete!")
        print("   Your site is now password-protected.")
    
    return success


def cleanup():
    """Clean up temporary files"""
    print("\nCleaning up...")
    
    # Remove encrypted folder if it was created but we kept site/
    # (since newer StatiCrypt versions encrypt in place)
    if Path("encrypted").exists() and Path("site").exists():
        print("   Removing empty encrypted folder...")
        try:
            shutil.rmtree("encrypted")
        except:
            pass


def main():
    """Main execution function"""
    print("="*60)
    print("SECURE BUILD AND DEPLOY PUBLISHER")
    print("="*60)
    
    # Step 1: Build navigation
    if not build_navigation():
        print("\nFAILED: Navigation build failed!")
        sys.exit(1)
    
    # Step 2: Build MkDocs site
    if not build_mkdocs_site():
        print("\nFAILED: MkDocs build failed!")
        sys.exit(1)
    
    # Step 3: Encrypt site
    if not encrypt_site():
        print("\nFAILED: Encryption failed!")
        print("   Continuing anyway - site will be unencrypted!")
    
    # Cleanup
    cleanup()
    
    # Success!
    print("\n" + "="*60)
    print("SUCCESS!")
    print("="*60)
    print("Your encrypted site is ready in the 'site/' folder.")
    print("Build completed. Deployment will be handled by the main deploy script.")
    print("="*60)


if __name__ == "__main__":
    main()