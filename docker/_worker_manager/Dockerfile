FROM python:3.4.3

# The build context is the whole Adama source code

# Needs:
# - rabbit (a RabbitMQ instance)
# - redis  (a Redis instance)

ADD . /adama
WORKDIR /adama/docker/shared/store
RUN pip install -r requirements.txt
ENV PYTHONPATH $PYTHONPATH:/adama/docker/shared/store

WORKDIR /adama/docker/shared/tools
RUN pip install -r requirements.txt
ENV PYTHONPATH $PYTHONPATH:/adama/docker/shared/tools

WORKDIR /adama/docker/worker_manager/app
RUN pip install -r requirements.txt

WORKDIR /

CMD ["python", "main.py"]
