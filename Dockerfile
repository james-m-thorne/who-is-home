FROM python:3.8-slim

RUN apt-get update \
&& apt-get install gcc -y

WORKDIR /app

COPY ./requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

COPY . .

ENTRYPOINT python ./src/main.py