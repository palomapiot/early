FROM python:latest

LABEL maintainer="paloma.piot@udc.es"

RUN apt update && apt-get install -y postgresql gcc python3 musl 

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt

#RUN pip3 install versiontools
RUN pip install -U spacy
RUN python -m spacy download en_core_web_lg
RUN pip3 install -r requirements.txt

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN useradd -ms /bin/bash user
USER user

CMD python manage.py runserver 0.0.0.0:$PORT