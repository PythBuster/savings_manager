# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os
import sys

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Savings Manager"
copyright = "2024, PythBuster"
author = "PythBuster"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# need this, spinx tries to find the python modules for code documentation
sys.path.insert(0, os.path.abspath("../../../src"))

extensions = ["sphinx.ext.autodoc", "sphinx_rtd_theme"]

templates_path = ["_templates"]
exclude_patterns = ["main.rst"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'bizstyle'
html_theme = "sphinx_rtd_theme"
# html_static_path = ['_static']
# html_theme_options = {
#    "sidebarwidth": 310,
# }
