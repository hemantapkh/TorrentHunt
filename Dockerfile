FROM ubuntu:20.04

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive

RUN apt -qq update

RUN apt -qq install -y python3 python3-pip build-essential bash

COPY . .

RUN pip3 install -r requirements.txt

CMD ["sh", "-c", "python3 migrations.py ; python3 torrenthunt.py"]
