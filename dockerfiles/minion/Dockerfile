FROM serfnode

MAINTAINER Walter Moreira <wmoreira@tacc.utexas.edu>

RUN apt-get install -y iptables
COPY handler /handler
COPY worker.conf /programs/
COPY minion_actor.conf /etc/supervisor/conf.d/
