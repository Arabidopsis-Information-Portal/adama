FROM python:3.4.3

# The build context is the whole Adama source code

ADD . /adama
WORKDIR /adama/docker/shared/store
RUN pip install -r requirements.txt
ENV PYTHONPATH $PYTHONPATH:/adama/docker/shared/store

WORKDIR /adama/docker/shared/tools
RUN pip install -r requirements.txt
ENV PYTHONPATH $PYTHONPATH:/adama/docker/shared/tools

WORKDIR /adama/docker/worker_base/python/app
RUN pip install -r requirements.txt

WORKDIR /

CMD ["python", "main.py"]
