#!/usr/bin/env python3
"""
build_nav.py - The Architect
Reads mkdocs.yml (base config) and creates mkdocs_base.yml with auto-generated navigation.
"""

import os
import yaml
from pathlib import Path


def scan_docs_folder(docs_path="docs"):
    """
    Recursively scan the docs folder and build a navigation structure.
    Returns a list suitable for MkDocs nav configuration.
    """
    nav = []
    docs_dir = Path(docs_path)
    
    if not docs_dir.exists():
        print("Warning: {} folder not found!".format(docs_path))
        return nav
    
    def build_nav_recursive(current_path, relative_to=docs_dir):
        """Recursively build navigation from folder structure"""
        items = []
        
        # Get all items in current directory
        try:
            entries = sorted(current_path.iterdir(), key=lambda x: (not x.is_file(), x.name.lower()))
        except PermissionError:
            return items
        
        for entry in entries:
            # Skip hidden files and __pycache__
            if entry.name.startswith('.') or entry.name == '__pycache__':
                continue
            
            relative_path = entry.relative_to(relative_to)
            
            if entry.is_file() and entry.suffix == '.md':
                # For markdown files, create a nav entry
                # Use filename without extension as the title
                title = entry.stem.replace('_', ' ').replace('-', ' ').title()
                
                # Special case: index.md becomes the folder name
                if entry.name.lower() == 'index.md':
                    if current_path == docs_dir:
                        title = "Home"
                    else:
                        title = current_path.name.replace('_', ' ').replace('-', ' ').title()
                
                items.append({title: str(relative_path).replace('\\', '/')})
                
            elif entry.is_dir():
                # For directories, recursively build nav
                folder_name = entry.name.replace('_', ' ').replace('-', ' ').title()
                sub_items = build_nav_recursive(entry, relative_to)
                
                if sub_items:
                    items.append({folder_name: sub_items})
        
        return items
    
    nav = build_nav_recursive(docs_dir)
    return nav


def update_mkdocs_base_yml(nav_structure):
    """
    Read mkdocs.yml (base config) and create mkdocs_base.yml with navigation.
    """
    base_file = Path("mkdocs.yml")
    output_file = Path("mkdocs_base.yml")
    
    # Load base configuration from mkdocs.yml
    if base_file.exists():
        with open(base_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
    else:
        print("ERROR: mkdocs.yml not found!")
        print("This file should contain your base configuration.")
        return False
    
    # Verify site_name exists
    if 'site_name' not in config:
        print("ERROR: mkdocs.yml must contain 'site_name'")
        return False
    
    # Update navigation
    config['nav'] = nav_structure
    
    # Write to mkdocs_base.yml
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print("Updated {} with {} top-level items".format(output_file, len(nav_structure)))
    return True


def main():
    """Main execution function"""
    print("Building navigation structure...")
    
    # Scan docs folder
    nav = scan_docs_folder("docs")
    
    if not nav:
        print("Warning: No markdown files found in docs/ folder!")
        print("Creating a basic navigation structure...")
        nav = [{'Home': 'index.md'}]
    
    # Update mkdocs_base.yml
    success = update_mkdocs_base_yml(nav)
    
    if success:
        print("Navigation build complete!")
        return 0
    else:
        print("Navigation build failed!")
        return 1


if __name__ == "__main__":
    exit(main())