FROM python:3.11.2-slim

WORKDIR /opt/torrenthunt

RUN apt-get -qq update

COPY app app
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3","app/torrenthunt.py"]
