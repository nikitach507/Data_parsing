FROM python:latest

WORKDIR /app

COPY main.py /app
COPY sample-data.json /app


RUN apt-get -y update && apt-get -y upgrade

RUN pip install psycopg2-binary

CMD ["python3", "main.py"]