# Installation


## Require software

1. docker-engine
https://docs.docker.com/engine/installation/
2. docker-compose
https://docs.docker.com/compose/install/


## Docker initialization

```
git clone https://github.com/savoirfairelinux/santropol-feast/
docker-compose build
docker-compose up
```
docker must be up and running at this point.

## Django initialization

You need the docker container_id to execute bash. You can get the container_id by running ```docker ps```.

```
docker exec -it [container_id] bash
python3 /django/santropolFeast/manage.py migrate
python3 /django/santropolFeast/manage.py createsuperuser
```

## Connection to application

To connect to the django application go to http://localhost:8000 .

##Troubleshooting
1. ```TERM environment not set``` https://github.com/dockerfile/mariadb/issues/3

