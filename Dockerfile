FROM python:3.5
LABEL maintainer "Ilya Shakhat <shakhat@gmail.com>"

RUN echo "deb http://httpredir.debian.org/debian jessie non-free" >> /etc/apt/sources.list \
    && apt-get update \
    && apt-get -y install --no-install-recommends \
        iperf \
        iperf3 \
        netperf \
        python-openstackclient \
    && apt-get clean

ADD . /opt/shaker/
RUN pip install -r /opt/shaker/requirements.txt flent
WORKDIR /opt/shaker/
RUN python setup.py install

VOLUME /artifacts

STOPSIGNAL SIGTERM

ENTRYPOINT ["/usr/local/bin/shaker-all-in-one", "--artifacts-dir", "/artifacts", "--log-dir", "/artifacts"]
