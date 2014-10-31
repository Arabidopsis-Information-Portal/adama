FROM common

RUN apt-get install -y python python-dev python-pip ipython
RUN pip install pika

ADD worker.py /root/worker.py
ADD tasks.py /root/tasks.py

EXPOSE 22

CMD []
ENTRYPOINT ["python", "/root/worker.py"]
