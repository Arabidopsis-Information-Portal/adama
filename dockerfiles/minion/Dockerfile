FROM ubuntu:14.04

MAINTAINER Walter Moreira <wmoreira@tacc.utexas.edu>

RUN apt-get update -y && \
    apt-get install -y python python-pip
RUN pip install serf_master
ADD serf /usr/bin/serf
ADD handler.py /

EXPOSE 7946

CMD ["serf", "agent", "-event-handler=/handler.py", "-tag", "role=minion"]
