FROM ubuntu

MAINTAINER Walter Moreira <wmoreira@tacc.utexas.edu>

RUN apt-get update -y && \
    apt-get install -y git libncurses5-dev git python3 python3-pip python3-dev

COPY adama-package/ /adama-package
WORKDIR adama-package/
RUN pip3 install -r requirements.txt
ENV MYPYPATH /adama-package/stubs
