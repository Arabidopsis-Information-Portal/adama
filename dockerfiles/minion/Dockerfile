FROM ubuntu:14.04

MAINTAINER Walter Moreira <wmoreira@tacc.utexas.edu>

RUN apt-get update -y && \
    apt-get install -y python python-pip iptables
RUN pip install serf_master
COPY serf /usr/bin/
COPY handler /handler

EXPOSE 7946

CMD ["serf", "agent", "-event-handler=/handler/handler.py", "-tag", "role=minion", "-log-level=debug"]
