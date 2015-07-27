FROM python:3.4.3

ADD . /adama
WORKDIR /adama/libraries/store
RUN python setup develop

WORKDIR /adama/docker/image_builder/app
RUN pip install -r requirements.txt

CMD ["python", "main.py"]
