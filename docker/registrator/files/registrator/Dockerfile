FROM python:3.4.3

# Needs:
# - rabbit (a RabbitMQ instance)
# - redis  (a Redis instance)


ADD . /

WORKDIR /modules/store
RUN pip install -r requirements.txt
ENV PYTHONPATH $PYTHONPATH:/modules/store

WORKDIR /modules/tools
RUN pip install -r requirements.txt
ENV PYTHONPATH $PYTHONPATH:/modules/tools


WORKDIR /app
RUN pip install -r requirements.txt

