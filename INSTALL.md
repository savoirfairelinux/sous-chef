Installation
==============

##Require software
===============
1. docker-engine
https://docs.docker.com/engine/installation/
2. docker-compose
https://docs.docker.com/compose/install/

##Python Dependancy
==============
1. django
2. mysqlclient

##Configuration
=============
1. git clone project
2. docker-compose build
3. docker-compose up
4. docker exec -it containerid (web django) bash
5. python3 /django/santropolFeast/manage.py migrate
6. python3 /django/santropolFeast/manage.py createsuperuser
