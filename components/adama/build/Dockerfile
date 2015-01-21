FROM serfnode

MAINTAINER Walter Moreira <wmoreira@tacc.utexas.edu>

COPY handler /handler

RUN apt-get update -y && \
    apt-get install -y git libncurses5-dev git python3 python3-dev python3-pip

COPY adama-package/ /adama-package
WORKDIR adama-package/
RUN pip3 install -r requirements.txt
