FROM ubuntu
RUN apt-get update
RUN apt-get install -y openssh-server
#RUN mkdir /var/run/sshd
#RUN mkdir -p /root/.ssh
#ADD coreos_id_rsa.pub /root/.ssh/authorized_keys
#RUN chmod -R 700 /root/.ssh
#RUN chown -R root:root /root/.ssh
RUN service ssh start
EXPOSE 22
#CMD ["/usr/sbin/sshd", "-D"]
