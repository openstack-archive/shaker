FROM python:3.5
MAINTAINER Ilya Shakhat <shakhat@gmail.com>

ADD . /opt/shaker/
RUN pip install -r /opt/shaker/requirements.txt
WORKDIR /opt/shaker/
RUN python setup.py install

VOLUME /artifacts

STOPSIGNAL SIGTERM

ENTRYPOINT ["/usr/local/bin/shaker-all-in-one", "--artifacts-dir", "/artifacts"]
