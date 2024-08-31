# Specify the base image for the environment
FROM ubuntu:20.04

# Authors of the image
LABEL authors="lnuernberg@bwh.harvard.edu"

# Remove any third-party apt sources to avoid issues with expiring keys.
RUN rm -f /etc/apt/sources.list.d/*.list

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Amsterdam
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Create a working directory and set it as the working directory
RUN mkdir /app /app/test /app/test/src /app/test/ref /app/output
WORKDIR /app

# Install system utilities and useful packages
RUN apt update && apt install -y --no-install-recommends \  
  wget \
  curl \
  jq \
  gcc \
  unzip \
  sudo \
  git \
  python3 \
  python3-pip

# Install system dependencies
RUN apt update && apt install -y --no-install-recommends \
  plastimatch \
  && rm -rf /var/lib/apt/lists/* 

# Install poetry and add to path
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:${PATH}"

# copy source code and poetry files
COPY ./medcmp /app/medcmp
COPY poetry.lock pyproject.toml README.md /app/

# Install dependencies
RUN poetry install

# Set the entrypoint
ENTRYPOINT ["poetry", "run", "medcmp"]