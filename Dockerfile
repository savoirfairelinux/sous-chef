FROM python:3.5
ENV PYTHONUNBUFFERED 1

# Create workdir and copy code
RUN mkdir /code
WORKDIR /code
COPY . /code/

# Install underlying debian dependencies
RUN apt-get update
RUN apt-get install curl gettext -y
RUN curl -sL https://deb.nodesource.com/setup_10.x | bash -
RUN apt-get install nodejs build-essential -y
RUN apt-get install binutils libproj-dev gdal-bin -y
RUN apt-get clean

# Install python dependencies
RUN pip3 install -r requirements.txt

# Install javascript dependencies
RUN npm install gulp -g
RUN cd /code/tools/gulp && npm install

# Generate and collect assets
RUN cd /code/tools/gulp && gulp
RUN python3 src/manage.py collectstatic --noinput

# Default entry point to gunicorn server, can be override by docker-compose
CMD cd src && /usr/local/bin/gunicorn sous_chef.wsgi:application -w 2 -b :8000

