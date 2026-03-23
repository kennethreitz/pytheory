import os
import sys
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(".."))

# Mock sounddevice so Sphinx can import pytheory.play without PortAudio
sys.modules["sounddevice"] = MagicMock()

project = "PyTheory"
copyright = "2026, Kenneth Reitz"
author = "Kenneth Reitz"
import pytheory
release = pytheory.__version__
version = pytheory.__version__

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
]

autodoc_member_order = "bysource"
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

templates_path = ["_templates"]
exclude_patterns = ["_build"]

html_theme = "alabaster"
html_theme_options = {
    "github_user": "kennethreitz",
    "github_repo": "pytheory",
    "github_banner": True,
    "github_button": True,
    "github_type": "star",
    "github_count": True,
    "description": "Music Theory for Humans",
    "extra_nav_links": {
        f"v{pytheory.__version__}": "https://pypi.org/project/pytheory/",
    },
    "show_powered_by": False,
}
html_static_path = ["_static"]
html_extra_path = ["CNAME"]
