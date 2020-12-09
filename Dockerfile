FROM python:latest

LABEL maintainer="paloma.piot@udc.es"

RUN apt update && apt-get install -y postgresql gcc python3 musl 

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt

RUN pip3 install -r requirements.txt 

RUN mkdir /app
WORKDIR /app
COPY ./app /app
EXPOSE 8000

RUN useradd -ms /bin/bash user
USER user

RUN python manage.py makemigrations && python manage.py migrate

CMD python manage.py runserver 0.0.0.0:$PORT