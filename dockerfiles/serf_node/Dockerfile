FROM ubuntu:14.04

MAINTAINER Walter Moreira <wmoreira@tacc.utexas.edu>

RUN apt-get update -y && \
    apt-get install -y python python-pip
RUN pip install serf_master
COPY serf /usr/bin/
COPY handler /handler

EXPOSE 7946 7373

CMD ["/handler/join.py"]
