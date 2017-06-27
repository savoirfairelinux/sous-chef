FROM python:3.5
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
ADD . /code/

# install underlying debian dependencies
RUN apt-get update
RUN apt-get install curl gettext -y
RUN curl -sL https://deb.nodesource.com/setup_8.x | bash -
RUN apt-get install nodejs build-essential -y
RUN apt-get install binutils libproj-dev gdal-bin -y
RUN apt-get clean

# install python dependencies
RUN pip3 install -r requirements.txt

# install javascript dependencies
RUN npm install gulp -g

# compile front-end "assets" (this should be unnecessary since they're basically just files, but hey, it's 2017)
# the 'rebuild node-sass' is a patch over a glitch which showed up recently;
# the tip that fixed it is from https://github.com/sass/node-sass/issues/1387#issuecomment-185451183
# perhaps it is not truly necessary.
run mkdir /code/src/sous_chef/static/
RUN python3 src/manage.py collectstatic --noinput
WORKDIR /code/tools/gulp
RUN npm install  # gulp dependencies
RUN gulp
WORKDIR /code/

# the default entrypoint for the container
# when this ends, the container ends, then restarts
# can be overridden in docker-compose.yml files
CMD python3 src/manage.py runserver 0.0.0.0:8000
