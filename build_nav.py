import os
import yaml
from pathlib import Path

exclude_files = ['404.md']

def scan_docs_folder(docs_path="docs"):
    docs_dir = Path(docs_path)
    if not docs_dir.exists():
        return []
    
    def build_nav_recursive(current_path, relative_to=docs_dir):
        items = []
        try:
            entries = sorted(current_path.iterdir(), key=lambda x: (not x.is_file(), x.name.lower()))
        except PermissionError:
            return items
        
        for entry in entries:
            if entry.name.startswith('.') or entry.name == '__pycache__':
                continue
            relative_path = entry.relative_to(relative_to)
            if entry.is_file() and entry.suffix == '.md' and entry.name not in exclude_files:
                title = entry.stem.replace('_', ' ').replace('-', ' ').title()
                if entry.name.lower() == 'index.md':
                    title = "Home" if current_path == docs_dir else current_path.name.title()
                items.append({title: str(relative_path).replace('\\', '/')})
            elif entry.is_dir():
                folder_name = entry.name.replace('_', ' ').replace('-', ' ').title()
                sub_items = build_nav_recursive(entry, relative_to)
                if sub_items:
                    items.append({folder_name: sub_items})
        return items
    return build_nav_recursive(docs_dir)

def update_mkdocs_base_yml(nav_structure):
    """
    Reads a clean mkdocs.yml, adds fresh navigation, 
    and saves the result to mkdocs_base.yml.
    """
    base_file = Path("mkdocs.yml")
    output_file = Path("mkdocs_base.yml")
    
    if not base_file.exists():
        print("ERROR: mkdocs.yml (template) not found!")
        return False
        
    with open(base_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f) or {}

    # This line replaces any existing 'nav' with the fresh scan
    config['nav'] = nav_structure 
    
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"Successfully created {output_file} with fresh navigation.")
    return True

if __name__ == "__main__":
    nav = scan_docs_folder("docs")
    if update_mkdocs_base_yml(nav):
        print("Navigation merged successfully!")