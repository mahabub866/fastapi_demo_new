# syntax=docker/dockerfile:1

FROM python:3.10.10-slim-buster
EXPOSE 8000
RUN apt-get update -y
RUN apt-get install -y python3-dev default-libmysqlclient-dev build-essential
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "-m" , "uvicorn", "main:app","--host=0.0.0.0"]

