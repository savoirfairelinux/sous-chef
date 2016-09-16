# Contributing to the frontend of Sous-Chef

First of all, thanks for reading this and taking time to contribute! :+1: We need volunteer developers to help this project grow.

The following is a set of guidelines for contributing to the frontend of Sous-Chef, which is hosted in the [Savoir-faire Linux organization](https://github.com/savoirfairelinux) on GitHub.
Feel free to propose changes to this document in a pull request.

If you haven't already, please join us on IRC: `#souschef` on Freenode.

## Useful resources

* [NPM](https://www.npmjs.com/)
* [GULP](http://gulpjs.com/)


## How can I contribute ?

### Code contribution

A pre-requisite is to have Sous-Chef installed on your machine.
The installation procedure is based on Docker and is described [on GitHub](https://github.com/savoirfairelinux/sous-chef/blob/dev/INSTALL.md).
To contribute to the frontend of Sous-chef, you also need to install npm and gulp in your machine.
The installation procedure of NPM is different for Windows / Mac OSX / Linux, so we recommend you to follow the procedure described in [NPM](https://docs.npmjs.com/getting-started/installing-node)
Once you have installed NPM follow the instruction to install [GULP](https://github.com/gulpjs/gulp/blob/master/docs/getting-started.md)

#### Modifying CSS and JavaScript files

All CSS and JavaScript files are in the directories `css` and `js`, if you modify an existing file,
you need to run `gulp` to generate the final file into sous-chef/static directory, you can also use
`gulp watch` so gulp will autodetect when you have made modification to the existing files and it will
generate the final file automatically. You need to be into the /tools/gulp directory to run `gulp`.

### If you need to add a new CSS file

You should rename you CSS file into a SCSS (for “Sassy CSS”) file, any valid CSS3 file is a valid SCSS file, so don't
worry if you don't know Sass. You should include your new file into the scss/main.scss file so it will be used
to generate the final CSS file.

### If you need to add a new JavaScript file

You should place your new file into the js directory and then edit the file /tools/gulp/gulpfile.js to add your
new file into the right task, so gulp will use your new file to generate the finals JavaScript files.

### If you need to add a plugin (Ex: jQuery plugin)

Place the images of the plugin (if there are any) into the frontend/images/vendor/name_of_jquery_plugin directory.
Place the css files of the plugin (if there are any) into the frontend/css/vendor/name_of_jquery_plugin directory.
Place the javascript files of the plugin (if there are any) into the frontend/js/vendor/name_of_jquery_plugin directory.
And follow the same procedure explained in the sections "If you need to add a new CSS file" and "If you need to add a new JavaScript file"

### If gulp task fails because there are some JavaScript error

You can use the task `gulp validate` that will show you in what file and line is the error, so it will be more easy
to fix.
