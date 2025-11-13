FROM python:3.13-slim 

RUN apt update && \
    apt install -y nginx && \
    apt install -y default-libmysqlclient-dev build-essential pkg-config

WORKDIR /app

COPY ./django_server /app
COPY ./nginx_server/default.conf /etc/nginx/conf.d/default.conf

RUN pip install -r requirements.txt

ENV SECRET_KEY='django-insecure-jbkd@l(3$6@ph&bprwp#c#rnkhg0$ci1_&3nuwl#m!bce9o%nc'

COPY run.sh .
RUN chmod +x run.sh
CMD ["./run.sh"]
