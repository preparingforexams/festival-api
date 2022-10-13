FROM python:3.10-slim

WORKDIR /usr/src/app

ENV PYTHONUNBUFFERED=1

ADD app app
ADD alembic alembic
ADD alembic.ini .
ADD main.py .
ADD requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD python -B -OO main.py
