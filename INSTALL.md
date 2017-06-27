# Installation

## Required dependencies

### Linux

As a first step, you must install the following dependencies:

1. **docker-engine**: https://docs.docker.com/engine/installation/
2. **docker-compose**: https://docs.docker.com/compose/install/

### OS X

As a first step, you must install **Docker For Mac**: https://docs.docker.com/docker-for-mac/install/

### Windows

For Windows 10, it is recommended to use **Docker For Windows**: https://docs.docker.com/docker-for-windows/install/ (**notice**: Hyper-V must be enabled. Follow the instructions during installation.) Make sure that Docker icon appears in task tray and prompts "Docker is running". You can then use `cmd` or `PowerShell` to run the following commands.

For older Windows versions, you may have to use **Docker Toolbox** (https://www.docker.com/toolbox) and you must run commands from the **docker quickstart terminal** (a shortcut on desktop).

## Docker initialization

```
$> git clone https://github.com/savoirfairelinux/sous-chef
$> cd sous-chef
$> docker-compose up
```

After this, test it worked by going to http://localhost:8000.

**Notice**: if you see the error "Can't connect to database" in `souschef_web_1`, try Ctrl+C and re-run `docker-compose up`.

To make changes to the running image, you could re-run it with `docker-compose up --build`, but to speed up development
you can instead loop-mount the `sous-chef/` directory into the container by running

```
$> docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

Similarly, you could use the production settings file that uses `gunicorn` to better handle load:

```
$> docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

## Django initialization

Unfortunately, the bulk of the Django configuration cannot happen until the containers are already built
and running, because it needs to talk to the database which is in a different container, managed by docker-compose.
So after you do the first build, you need to manually do some more steps.

In your console:

```
$> docker-compose exec web bash
```

Then you should be inside a container as you can see, e.g., `root@d157a3f57426:/code#`. Then run:

```
$> cd src

# Run existing migrations
$> python3 manage.py migrate

# Create a user with administrator privileges
$> python3 manage.py createsuperuser

# Optional: Load the initial data set
$> python3 manage.py loaddata sample_data
```

## (Optional) Generate frontend assets

You do not need to run these commands to deploy Sous-Chef, but if during development
you make changes to anything in the frontend you will need to know at least gulp.

[gulp](http://gulpjs.com/) is a javascript-based build system.
We use it to compile and optimize files from `src/frontend/` to `src/sous_chef/static/`.
We specifically use it to compile scss to css, javascript to minified javascript,
and images to further-compressed images.

To run gulp, use:

```
$> docker-compose exec web sh -c "cd tools/gulp && gulp"
```

If you have an error with this command, try deleting the folder `tools/gulp/node_modules` completely and rerun it. If the problem still exists, please let us know, including the versions of node, npm, and gulp that you have.

[collectstatic](https://docs.djangoproject.com/en/1.11/ref/contrib/staticfiles/#collectstatic) is similar, but built into Django.
We are not using it to manage our own static files, but some of our Django dependencies might need this to be run.

## Connection to application

A Django development server is automatically started unless you have run with production settings. It is accessible at `http://localhost:8000`.

## Backup and restore database

The database content is stored in a Docker named volume that is not directly accessible.

**For backup**, running:

```
$> docker run --rm --volumes-from souschef_db_1 -v $(pwd):/backup ubuntu tar cvf /backup/backup.tar /var/lib/mysql
```

In Windows console, running:

```
$> docker run --rm --volumes-from souschef_db_1 -v %cd%:/backup ubuntu tar cvf /backup/backup.tar /var/lib/mysql
```

`souschef_db_1` is the container's name that can be found by running `docker ps`. This command creates a temporary Ubuntu container, connects it with both the volume that `souschef_db_1` uses and current directory on host machine. You will find `backup.tar` in current directory after this command.

**For restoring**:

```
$> docker run --rm --volumes-from souschef_db_1 -v $(pwd):/backup ubuntu bash -c "cd /var/lib/mysql && tar xvf /backup/backup.tar --strip 1"
```

In Windows console:

```
$> docker run --rm --volumes-from souschef_db_1 -v %cd%:/backup ubuntu bash -c "cd /var/lib/mysql && tar xvf /backup/backup.tar --strip 1"
```

Refs: https://docs.docker.com/engine/tutorials/dockervolumes/#backup-restore-or-migrate-data-volumes

## Troubleshooting

1. ```TERM environment not set```: https://github.com/dockerfile/mariadb/issues/3
2. ```listen tcp 0.0.0.0:8000: bind: address already in use``` : an another application already uses the 8000 port. Vagrant applications often use the same port for instance. Locate the application and shut it down, or select an other port.
3. ```Web server is up and running, but no answer after Django initialization``` : restart your container.
4. ```Static files fail to load when using Nginx server in development mode (docker-compose up)```: run ```docker-compose exec web python src/manage.py collectstatic```
