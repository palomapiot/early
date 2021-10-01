###
#    Copyright 2020-2021 Paloma Piot Pérez-Abadín
	
#	This file is part of early.
#    early is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#    early is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    You should have received a copy of the GNU General Public License
#   along with early.  If not, see <https://www.gnu.org/licenses/>.
###

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

CMD python manage.py runserver 0.0.0.0:8000