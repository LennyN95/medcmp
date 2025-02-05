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
  ca-certificates \
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

# Install uv (https://docs.astral.sh/uv/guides/integration/docker/#installing-uv)
# COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"


# copy source code and pyproject files
COPY ./medcmp /app/medcmp
COPY uv.lock pyproject.toml README.md /app/

# setup python environment
RUN uv sync

# set the entrypoint to run medcmp
ENTRYPOINT ["uv", "run", "medcmp"]