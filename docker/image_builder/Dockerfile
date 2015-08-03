FROM python:3.4.3

ADD . /adama
WORKDIR /adama/docker/shared/store
RUN pip install -r requirements.txt
ENV PYTHONPATH $PYTHONPATH:/adama/docker/shared/store

WORKDIR /adama/docker/image_builder/app
RUN pip install -r requirements.txt

WORKDIR /

CMD ["python", "main.py"]
