FROM ubuntu:22.04

USER root

RUN apt-get -y update && \
    DEBIAN_FRONTEND=noninteractive apt-get -qq install \
    git vim pip wget npm

# Upgrate python setuptools version
RUN pip install --upgrade --user setuptools==75.8.0

#
RUN apt install -y swig cmake net-tools byobu
RUN pip3 install pipenv

#
RUN npm cache clean -f
RUN npm install -g n
RUN n 16.19.1
RUN npm install --global yarn pm2 pkg

# Create a non-root user
RUN useradd -ms /bin/bash chunwei

# Switch to non-root user
USER chunwei

WORKDIR /home/chunwei