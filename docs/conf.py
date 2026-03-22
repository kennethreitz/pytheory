import os
import sys
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(".."))

# Mock sounddevice so Sphinx can import pytheory.play without PortAudio
sys.modules["sounddevice"] = MagicMock()

project = "PyTheory"
copyright = "2024, Kenneth Reitz"
author = "Kenneth Reitz"
release = "0.2.0"

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
html_title = "PyTheory"
html_static_path = ["_static"]
html_extra_path = ["CNAME"]
