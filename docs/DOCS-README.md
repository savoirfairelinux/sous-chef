## From within the docs folder, run these two commands to re-generate the documentation:
# sphinx-apidoc -f -o [output] [input] builds .rst files for the modules found at [input] and saves them to [output].
sphinx-apidoc -f -o source ../django/SantropolFeast/

# make html uses the .rst files to build the html version of the docs
make html
