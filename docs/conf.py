import importlib.metadata

project = "bad_tools"
copyright = "2023, Thomas A Caswell"
author = "Thomas A Caswell"
version = release = importlib.metadata.version("bad_tools")

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "sphinx_copybutton",
]

source_suffix = [".rst", ".md"]
exclude_patterns = [
    "_build",
    "**.ipynb_checkpoints",
    "Thumbs.db",
    ".DS_Store",
    ".env",
    ".venv",
]

html_theme = "furo"

myst_enable_extensions = [
    "colon_fence",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

nitpick_ignore = [
    ("py:class", "_io.StringIO"),
    ("py:class", "_io.BytesIO"),
]

always_document_param_types = True
