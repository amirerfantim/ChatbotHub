FROM python:3.11-slim

COPY ./requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY ./ /app

VOLUME /data=/data

CMD python /app/manage.py makemigration

CMD python /app/manage.py migrate

CMD python /app/manage.py runserver

