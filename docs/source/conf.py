"""
Sphinx configuration for the Onomasticon documentation site.
"""

from __future__ import annotations

import os
import sys
from datetime import date
from importlib import metadata
from pathlib import Path

try:
    import tomllib  # py311+
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))


def _docs_version() -> str:
    """
    Resolve the package version for the docs site.
    """
    env_version = os.getenv("DOCS_VERSION")
    if env_version:
        return env_version

    try:
        return metadata.version("onomasticon")
    except metadata.PackageNotFoundError:
        pyproject_path = ROOT / "pyproject.toml"
        data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
        version_value = data.get("project", {}).get("version")
        if isinstance(version_value, str) and version_value.strip():
            return version_value.strip()

    return "0.0.0"


project = "Onomasticon"
copyright = f"{date.today().year}, Santiago Rincon"
author = "Santiago Rincon"

version = _docs_version()
release = version

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    "sphinx_design",
]

templates_path = ["_templates"]
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
]

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "fieldlist",
]

autosummary_generate = True
autodoc_typehints = "none"
autodoc_member_order = "bysource"
nitpick_ignore = [
    ("py:obj", "onomasticon.onomasticon.ImplementationT"),
]

html_theme = "furo"
html_title = "Onomasticon"

REPO_URL = "https://github.com/rincorpes/onomasticon"
DOCS_URL = f"{REPO_URL}/tree/main/docs"
PYPI_URL = "https://pypi.org/project/onomasticon/"

html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "#0B6E4F",
        "color-brand-content": "#135D66",
        "color-background-secondary": "#F6FAF8",
    },
    "dark_css_variables": {
        "color-brand-primary": "#66D19E",
        "color-brand-content": "#7FD8E0",
        "color-background-primary": "#101614",
        "color-background-secondary": "#17201D",
        "color-code-background": "#0D1311",
    },
    "footer_icons": [
        {
            "name": "GitHub",
            "url": REPO_URL,
            "html": "",
            "class": "fa-brands fa-github",
        },
        {
            "name": "Docs",
            "url": DOCS_URL,
            "html": "",
            "class": "fa-solid fa-book",
        },
        {
            "name": "PyPI",
            "url": PYPI_URL,
            "html": "",
            "class": "fa-solid fa-cube",
        },
    ],
}
