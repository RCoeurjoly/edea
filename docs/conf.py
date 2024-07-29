import importlib.metadata
import os
import sys
from dataclasses import asdict
from datetime import datetime

from sphinxawesome_theme import LinkIcon, ThemeOptions, postprocess  # type: ignore


sys.path.insert(0, os.path.abspath(".."))

distribution = importlib.metadata.distribution("edea")
project = distribution.name
release = distribution.metadata["version"]
author = "EDeA Dev Team"
license = distribution.metadata["license"]
copyright = f"{datetime.now().year}, {author} under {license}."


extensions = [
    "myst_parser",
    "sphinx_favicon",
    "sphinx_inline_tabs",
    "sphinx_last_updated_by_git",
    "sphinx_sitemap",
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinxcontrib.asciinema",
    "sphinxext.opengraph",
]

coverage_statistics_to_stdout = True

templates_path = ["templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


html_static_path = ["_static"]
html_baseurl = "https://edea-dev.gitlab.io/edea/latest/"
html_css_files = ["custom.css"]
html_theme = "sphinxawesome_theme"
html_permalinks_icon = postprocess.Icons.permalinks_icon
html_theme_options = asdict(
    ThemeOptions(
        awesome_external_links=True,
        awesome_headerlinks=True,
        extra_header_link_icons={
            "repository on GitLab": LinkIcon(
                link="https://gitlab.com/edea-dev/edea",
                icon=open("gitlab.svg").read(),
            )
        },
    )
)

autodoc_type_aliases = {
    "CanonicalLayerName": "edea.kicad.pcb.layer.CanonicalLayerName",
}
autodoc_member_order = "bysource"

viewcode_follow_imported_members = True


favicons = [
    {"sizes": "16x16", "href": "favicon-16x16.png"},
    {"sizes": "32x32", "href": "favicon-32x32.png"},
]

ogp_description_length = 0
ogp_site_url = "https://edea-dev.gitlab.io/edea/latest/"
