#FROM python:2.7-alpine
FROM python:3.5.2-alpine
# todo: change starting point to this
#FROM amancevice/pandas:0.21.0-python3


# We want proper container logging
ENV PYTHONUNBUFFERED 1

EXPOSE 5432
EXPOSE 80

RUN apk add --no-cache --virtual .build-deps alpine-sdk \
    mariadb-dev \
    libffi-dev


COPY requirements.txt /etc/requirements.txt

# https://stackoverflow.com/questions/46711990/error-pg-config-executable-not-found-when-using-docker
RUN apk update && \
 apk add postgresql-libs && \
 apk add --virtual .build-deps gcc python3-dev musl-dev postgresql-dev

RUN apk add libxml2-dev


RUN pip install pandas
RUN pip install numpy


RUN pip install -r /etc/requirements.txt

# Set working directory to project
WORKDIR /gmail_metrics
COPY client_secret.json /gmail_metrics/.
COPY gmail_metrics_auth.json /gmail_metrics/.
COPY gmail_api_quickstart.py /gmail_metrics/.
COPY gmail_metrics_collector.py /gmail_metrics/.

##########run python setup.py build_ext --inplace --force

CMD ["python", "/gmail_metrics/gmail_metrics_collector.py"]
