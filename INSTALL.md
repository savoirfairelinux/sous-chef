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
$> docker-compose build
$> docker-compose up
```

**Notice**: if you see the error "Can't connect to database" in `souschef_web_1`, try Ctrl+C and re-run `docker-compose up`.

(Optional) Running docker-compose with production settings:

```
$> docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

## Django initialization

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

## Generate Django assets using gulp

### Run gulp

**From container:**

```
$> docker-compose exec web sh -c "cd tools/gulp && npm install --unsafe-perm && gulp"
```

Or **from host machine:**

```
$> cd tools/gulp && npm install --unsafe-perm && gulp

# If you don't have the gulp command, try: 
$> cd tools/gulp && node node_modules/gulp/bin/gulp.js
```

Please rest assured that the "unsafe-perm" option will not bring any security risk to sous-chef. The Node.js packages that we are installing here are only used for generating static files, such as images, CSS, JavaScript, etc., and will never be executed from external.

If you have an error with this command, try deleting the folder `tools/gulp/node_modules` completely and rerun it. If the problem still exists, please let us know.


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

In Windows console, replace `$(pwd)` as `%cd%`.

Refs: https://docs.docker.com/engine/tutorials/dockervolumes/#backup-restore-or-migrate-data-volumes

## Troubleshooting

1. ```TERM environment not set```: https://github.com/dockerfile/mariadb/issues/3
2. ```listen tcp 0.0.0.0:8000: bind: address already in use``` : an another application already uses the 8000 port. Vagrant applications often use the same port for instance. Locate the application and shut it down, or select an other port.
3. ```Web server is up and running, but no answer after Django initialization``` : restart your container.
4. ```Static files fail to load when using Nginx server in development mode (docker-compose up)```: run ```docker-compose exec web python src/manage.py collectstatic```
