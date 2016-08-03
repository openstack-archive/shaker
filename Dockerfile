FROM python:3.5
MAINTAINER Ilya Shakhat <shakhat@gmail.com>

ADD . /opt/shaker/
RUN pip install -r /opt/shaker/requirements.txt
WORKDIR /opt/shaker/
RUN python setup.py install

EXPOSE 5999

VOLUME /artifacts

STOPSIGNAL SIGTERM

ENTRYPOINT ["/usr/local/bin/shaker-all-in-one", "--artifacts-dir", "/artifacts"]
