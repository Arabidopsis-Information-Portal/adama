# Javascript worker image

FROM common

RUN apt-get install -y python-software-properties python g++ make
RUN add-apt-repository -y ppa:chris-lea/node.js
RUN apt-get update
RUN apt-get install -y nodejs

ENV NODE_PATH /usr/lib/node_modules

RUN npm install -g amqplib

ADD worker.js /root/worker.js

CMD []
ENTRYPOINT ["node", "/root/worker.js"]
