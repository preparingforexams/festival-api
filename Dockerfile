FROM python:3.10-slim

WORKDIR /usr/src/app

ENV PYTHONUNBUFFERED=1

ADD telegram_bot telegram_bot
ADD main.py .
ADD requirements.txt .
ADD setup.py .

RUN pip install --no-cache-dir -r requirements.txt

CMD python -B -OO main.py
