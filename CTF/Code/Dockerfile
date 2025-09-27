FROM python:3.10-alpine

WORKDIR /app

EXPOSE  5000
ENV FLASK_APP=app.py

RUN mkdir -p /app/uploads
COPY ./app.py /app
COPY ./flag.txt /app
COPY ./secrets.txt /app/uploads
COPY ./requirements.txt /app
COPY ./letter.txt /app/uploads


RUN pip install -r requirements.txt

ENTRYPOINT ["flask"]
CMD ["run", "--host", "0.0.0.0"]

