# Common image for all containers

FROM phusion/baseimage
ENV HOME /root
RUN /etc/my_init.d/00_regen_ssh_host_keys.sh

RUN apt-get update
RUN apt-get install -y build-essential software-properties-common python-software-properties

# install ssh key
ADD id_rsa.pub /tmp/id_rsa.pub
RUN cat /tmp/id_rsa.pub >> /root/.ssh/authorized_keys && rm /tmp/id_rsa.pub
