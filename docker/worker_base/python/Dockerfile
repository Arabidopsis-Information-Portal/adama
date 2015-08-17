FROM common

RUN apt-get update
RUN apt-get install -y python python-dev python-pip ipython
RUN pip install pika redis pyzmq

ADD worker.py /root/worker.py
ADD tasks.py /root/tasks.py
ADD adamalib.py /root/adamalib.py
ADD store.py /root/store.py
ADD service.py /root/service.py

EXPOSE 22

CMD []
ENTRYPOINT ["python", "/root/worker.py"]
