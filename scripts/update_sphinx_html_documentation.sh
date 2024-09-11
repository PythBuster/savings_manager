#!/bin/bash

# how to generate sphinx doc from docstrings (autodoc)
# see: https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#module-sphinx.ext.autodoc

#mv ../src/__init__.py ../src/__init__.TMP
cd "../docs/sphinx"
poetry run sphinx-apidoc -f -o source/ ../../src

make html
cd "../../scripts"
#mv ../src/__init__.TMP ../src/__init__.py