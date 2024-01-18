FROM ubuntu:20.04

# install dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# install python dependencies

# copy source code
COPY . /app

# set working directory
WORKDIR /app