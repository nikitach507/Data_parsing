FROM python:alpine

ADD . /app

RUN pip install psycopg2-binary

WORKDIR /app

COPY sample-data.json .
COPY main.py .

CMD ["python", "./main.py"]
