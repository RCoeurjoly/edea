import importlib.metadata
import os
import re
import sys
from dataclasses import asdict
from datetime import datetime

from sphinxawesome_theme import LinkIcon, ThemeOptions

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

templates_path = ["templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_static_path = ["_static"]
html_theme = "sphinxawesome_theme"
html_theme_options = asdict(
    ThemeOptions(
        awesome_external_links=True,
        awesome_headerlinks=True,
        extra_header_link_icons={
            "GitLab": LinkIcon(
                link="https://gitlab.com/edea-dev/edea",
                icon=open("gitlab.svg").read(),
            )
        },
    )
)

autodoc_type_aliases = {
    "CanonicalLayerName": "edea.types.pcb.layer.CanonicalLayerName",
}
