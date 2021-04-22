FROM python:3.8-slim

RUN apt-get update && apt-get install arp-scan -y

WORKDIR /app

COPY ./requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

COPY ./src ./src

ENTRYPOINT python ./src/main.py