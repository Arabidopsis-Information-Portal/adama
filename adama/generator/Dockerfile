FROM ubuntu

RUN apt-get update -y
RUN apt-get install -y python python-pip git
RUN pip install cookiecutter click blessings flask

WORKDIR /
RUN git clone https://github.com/Arabidopsis-Information-Portal/adama.git
WORKDIR /adama
RUN python setup.py install

WORKDIR /tmp
RUN git clone https://github.com/audreyr/cookiecutter.git
WORKDIR /tmp/cookiecutter
RUN python setup.py install

RUN chmod +x /adama/adama/generator/generator.py
RUN ln -s /adama/adama/generator/generator.py /generator

WORKDIR /target

CMD ["/generator"]
