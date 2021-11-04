FROM python:3.8-slim-buster

WORKDIR /broker

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 5005 5006 5007