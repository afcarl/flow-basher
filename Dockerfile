FROM python:2.7
MAINTAINER AJ Bowen <aj@soulshake.net>

RUN apt-get update && apt-get install -y \
    libgtk-3.0 \
    libgconf-2-4 \
    libnss3 \
    libasound2 \
    libgtk2.0-0

RUN pip install --upgrade \
    pip \
    IPython \
    requests

RUN wget https://spideroak.com/releases/semaphor/debian \
    && dpkg -i debian \
    && rm -rf debian

RUN git clone https://github.com/SpiderOak/flow-python.git
WORKDIR flow-python
RUN pip install .

COPY . /src
WORKDIR /src
ENTRYPOINT ["python", "/src/basher.py"]
