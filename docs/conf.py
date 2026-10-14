# Sphinx configuration for the bamboo documentation.
# Build with:  sphinx-build -b html docs docs/_build/html

project = "bamboo"
author = "Prakriti Gupta"
copyright = "2026, Prakriti Gupta"
release = "0.1.0"
version = release

extensions = ["sphinxcontrib.mermaid"]

templates_path = []
exclude_patterns = ["_build"]

html_theme = "shibuya"
html_static_path = []
html_theme_options = {
    "github_url": "https://github.com/CaltechOpticalObservatories/bamboo",
}
html_context = {
    "source_type": "github",
    "source_user": "CaltechOpticalObservatories",
    "source_repo": "bamboo",
    "source_version": "main",
    "source_docs_path": "/docs/",
}
