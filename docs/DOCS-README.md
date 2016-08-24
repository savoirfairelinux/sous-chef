# How to build the HTML version of the docs:
You will need to install the sphinx package.  Then, from a terminal within the docs folder, run the commands given for your system to regenerate the documentation.

## Non-Windows:
```
$ make html
```
## Windows:
```
$ sphinx-apidoc -f -o source ../src/ ../src/*/migrations
$ make html
```
