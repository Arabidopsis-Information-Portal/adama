FROM serfnode

MAINTAINER Walter Moreira <wmoreira@tacc.utexas.edu>

COPY handler /handler

RUN apt-get update -y && \
    apt-get install -y git libncurses5-dev git

COPY adama-package/ /adama-package
WORKDIR adama-package/
RUN pip install -r requirements.txt
