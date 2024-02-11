cd "../docs/sphinx"
poetry run sphinx-apidoc -f -o source/ ../../src
poetry run sphinx-build source build
