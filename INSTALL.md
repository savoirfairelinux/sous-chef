Instalation
==============

Logiciel requis
===============

1. docker-engine
2. docker-compose

Dependancy
==============
1. django
2. mysqlclient

Install
=============
1. git clone project
2. docker-compose build
3. docker-compose up
4. docker exec -it containerid bash
5. python3 /django/santropolFeast/manage.py migrate
6. python3 /django/santropolFeast/manage.py createsuperuser
