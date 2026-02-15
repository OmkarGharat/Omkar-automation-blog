# Welcome to MkDocs

For full documentation visit [mkdocs.org](https://www.mkdocs.org).

# Installation

1. Create a new folder for the project
2. run these commands

```
pip install mkdocs-material
pip install "mkdocs-material[imaging]"
pip install mkdocs-macros-plugin
pip install watchdog
pip install mkdocs-toggle-sidebar-plugin
pip install pymdown-extensions
pip install pyyaml

then mkdocs new .

then mkdocs serve (to run the code on local machine)

mkdocs serve --livereload (to run the code on local machine with live reloading)
```

## Commands

- `mkdocs new [dir-name]` - Create a new project.
- `mkdocs serve` - Start the live-reloading docs server.
- `mkdocs build` - Build the documentation site.
- `mkdocs -h` - Print help message and exit.
- ` mkdocs serve` - Start the server.
- `mkdocs serve --livereload` -- Recommended for development.

# For Local Build

To run python file like build_nav.py run it as python build_nav.py

then mkdocs build --clean

then mkdocs serve

---
