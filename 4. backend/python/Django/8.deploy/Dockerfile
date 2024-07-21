# https://hub.docker.com/layers/library/python/3.12-alpine/images/sha256-07728be3c9b53172e16c2eb6917e31775a8b349d22c5c85adeb4b94d960647a5
FROM python:3.12-alpine

RUN pip install --upgrade pip

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./django_server /app

WORKDIR /app

COPY ./entrypoint.sh /
ENTRYPOINT ["sh", "/entrypoint.sh"]