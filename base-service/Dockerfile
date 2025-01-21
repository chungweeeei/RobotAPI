FROM ubuntu:22.04

USER root

RUN apt-get -y update && \
    DEBIAN_FRONTEND=noninteractive apt-get -qq install \
    git vim pip

RUN pip install --upgrade --user setuptools==58.0.0

# fastdds dependency
RUN apt install -y swig cmake net-tools byobu
RUN pip3 install colcon-common-extensions
RUN pip3 install vcstool
RUN pip3 install pipenv

# Create a non-root user
RUN useradd -ms /bin/bash chunwei

# Switch to non-root user
USER chunwei

WORKDIR /home/chunwei