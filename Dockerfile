FROM amancevice/pandas:0.21.0-python3

# We want proper container logging
ENV PYTHONUNBUFFERED 1

EXPOSE 8125/udp
EXPOSE 5432
EXPOSE 80

COPY requirements.txt /etc/requirements.txt
RUN pip install -r /etc/requirements.txt

# Set working directory to project
RUN mkdir -p /gmail_metrics
WORKDIR /gmail_metrics
COPY client_secret.json /gmail_metrics/
COPY gmail_metrics_auth.json /gmail_metrics/
COPY gmail_api_quickstart.py /gmail_metrics/
COPY gmail_metrics_collector.py /gmail_metrics/

CMD ["python", "/gmail_metrics/gmail_metrics_collector.py"]

