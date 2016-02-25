<H1>Installation


<H3>Require software

1. docker-engine
https://docs.docker.com/engine/installation/
2. docker-compose
https://docs.docker.com/compose/install/

<H3>Python Dependancy

1. django
2. mysqlclient

<H3>Configuration

1. git clone project
2. docker-compose build
3. docker-compose up
4. docker exec -it containerid (web django) bash
5. python3 /django/santropolFeast/manage.py migrate
6. python3 /django/santropolFeast/manage.py createsuperuser

<H3>Troubleshooting
1. "TERM environment not set"
https://github.com/dockerfile/mariadb/issues/3
2. "Cant connect to docker" Verify that you are root or sudo
