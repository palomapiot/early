FROM python:3.7-alpine
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN pip install -r requirements.txt

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN adduser -D user
USER user

CMD python manage.py runserver 0.0.0.0:$PORT