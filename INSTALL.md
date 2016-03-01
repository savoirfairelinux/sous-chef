# Installation

## Required dependencies

As a first step, you must install the following dependencies:

1. **docker-engine**: https://docs.docker.com/engine/installation/
2. **docker-compose**: https://docs.docker.com/compose/install/

## Docker initialization

```
$> git clone https://github.com/savoirfairelinux/santropol-feast/
$> docker-compose build
$> docker-compose up
```
Docker must be up and running at this point.

## Django initialization

You need the Docker **container ID** to run the next steps. You can get the container_id by running ```docker ps```.
Ex: *44fcfefb015e*

```
docker exec -it [container_id] bash
python3 django/santropolFeast/manage.py migrate
python3 django/santropolFeast/manage.py createsuperuser
```

## Connection to application

You should now be ready to run the Django application by pointing your browser to **http://localhost:8000**.

## Troubleshooting

1. ```TERM environment not set```: https://github.com/dockerfile/mariadb/issues/3
2. ```listen tcp 0.0.0.0:8000: bind: address already in use``` : an another application already uses the 8000 port. Vagrant applications often use the same port for instance. Locate the application and shut it down, or select an other port.

