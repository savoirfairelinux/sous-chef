# Installation

## Required dependencies

### Linux

As a first step, you must install the following dependencies:

1. **docker-engine**: https://docs.docker.com/engine/installation/
2. **docker-compose**: https://docs.docker.com/compose/install/

Then continue to the docker initialization step.

### OS X

As a first step, you must install the following dependencies:

1. **Docker Toolbox**: https://www.docker.com/toolbox

You must do the next set of command from the docker quickstart terminal.

Then continue to the docker initialization step.

### Windows

As a first step, you must install the following dependencies:

1. **Docker Toolbox** :https://www.docker.com/toolbox

**Notice**: Virtualisation must be enable on your computer

You must do the next set of command from the docker quickstart terminal.

Then continue to the docker initialization step.

## Docker initialization

```
$> git clone https://github.com/savoirfairelinux/sous-chef
$> docker-compose build
$> docker-compose up
```

If you want to run docker-compose with the production settings

```
$> docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

Docker must be up and running at this point.

## Django initialization

You need the Docker **container ID** to run the next steps. You can get the container_id by running ```docker ps```.
Ex: *44fcfefb015e*

```
docker exec -it [container_id] bash

# Move to the application root dir
cd src

# Run development server
python manage.py runserver 0.0.0.0:8080

# Access to the development server
http://0.0.0.0:8080

# Access to Nginx server
http://127.0.0.1

# Run existing migrations
python manage.py migrate

# Create a user with administrator privileges
python manage.py createsuperuser

# Load the initial data set
python3 manage.py loaddata routes client_options delivery_initial_data

```

## Connection to application


You should now be ready to run the Django application by pointing your browser to the container address.

On Linux and OS X, open http://localhost:8000.

On Windows, use the container IP address.

## Troubleshooting

1. ```TERM environment not set```: https://github.com/dockerfile/mariadb/issues/3
2. ```listen tcp 0.0.0.0:8000: bind: address already in use``` : an another application already uses the 8000 port. Vagrant applications often use the same port for instance. Locate the application and shut it down, or select an other port.
3. ```Web server is up and running, but no answer after Django initialization``` : restart your container.
4. ```Static files fail to load when using Nginx server in development mode (docker-compose up)```: run ```docker-compose exec web python src/manage.py collectstatic```
