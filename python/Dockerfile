FROM common
ENV HOME /root
RUN apt-get install -y python python-dev python-pip ipython
RUN pip install pika

ADD worker.py /root/worker.py

EXPOSE 22

CMD []
ENTRYPOINT ["/sbin/my_init", "--", "python", "/root/worker.py"]