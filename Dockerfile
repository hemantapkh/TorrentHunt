FROM ubuntu:latest

WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=America/Los_Angeles

RUN apt-get -qq update --fix-missing 

RUN apt-get -qq install -y git wget curl busybox python3 python3-pip locales

RUN apt install python3-pip
RUN pip3 install psycopg2-binary 

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

 
COPY . .

CMD ["bash","start.sh"]
