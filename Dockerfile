FROM python:3.5
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN apt-get update
RUN apt-get install curl gettext -y
RUN curl -sL https://deb.nodesource.com/setup_6.x | bash -
RUN apt-get install nodejs build-essential -y
RUN apt-get install binutils libproj-dev gdal-bin -y
RUN pip3 install -r requirements.txt
RUN npm install gulp -g
ADD . /code/
RUN apt-get clean
