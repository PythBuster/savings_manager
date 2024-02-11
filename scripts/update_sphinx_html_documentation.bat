move ../src/__init__.py ../src/__init__.TMP
cd "../docs/sphinx"
poetry run sphinx-apidoc -f -o source/ ../../src

poetry run sphinx-build source build
cd "../../scripts"
move ../src/__init__.TMP ../src/__init__.py