FROM ubuntu:14.04

MAINTAINER Walter Moreira <wmoreira@tacc.utexas.edu>

RUN apt-get update -y && \
    apt-get install -y python python-dev python-pip supervisor git
RUN apt-get install -y libzmq-dev
RUN pip install serf_master fig jinja2 ipython
RUN echo
WORKDIR /tmp
RUN git clone -b py2.7 https://github.com/waltermoreira/mischief.git
WORKDIR /tmp/mischief
RUN python setup.py install

WORKDIR /
COPY serf /usr/bin/
COPY handler /handler
COPY serfnode.conf /etc/supervisor/conf.d/
COPY programs /programs

EXPOSE 7946 7373

CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
