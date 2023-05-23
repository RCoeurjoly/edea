import importlib.metadata
import os
import re
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(".."))

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

distribution = importlib.metadata.distribution("edea")
project = distribution.name
release = distribution.metadata["version"]
license = distribution.metadata["license"]
author = "Elen Eisendle <ln@calcifer.ee>, Kaspar Emanuel <kaspar@kitspace.org>, Abdulrhmn Ghanem <abdoghanem160@gmail.com>, and contributors"
copyright = f'{datetime.now().year}, {re.sub(r" <[^>]+>", "", author)} under {license}.'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    # "sphinxcontrib.autodoc_pydantic",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_static_path = ["_static"]
html_theme = "sphinxawesome_theme"

autodoc_type_aliases = {
    "CanonicalLayerName": "edea.types.pcb_layers.CanonicalLayerName",
}
