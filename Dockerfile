# syntax=docker/dockerfile:1

###########################
# Build Image
###########################
FROM python:3.10-slim-bullseye
ARG USERNAME=app
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Required postgresql lib & compiler for psycopg2 build
RUN apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get -y install libpq-dev gcc make \
    && useradd -r -d /app -s /bin/bash -U -u $USER_UID $USERNAME

COPY --chown=$USER_UID:$USER_GID . /app/

USER $USERNAME
WORKDIR /app

COPY requirements.txt requirements-dev.txt /app/
RUN pip3 install --user -r requirements.txt \
    && pip3 install --user -r requirements-dev.txt
ENV PATH="${PATH}:/app/.local/bin"
RUN make clean && make && make clean

###########################
# Runtime Image
###########################
FROM python:3.10-slim-bullseye
ARG USERNAME=app
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Only include postgres runtime
RUN apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -rm -d /app -s /bin/bash -U -u $USER_UID $USERNAME
COPY --from=0 --chown=$USER_UID:$USER_GID /app/.local/ /app/.local/
COPY --from=0 --chown=$USER_UID:$USER_GID /app/project/ /app/
RUN chmod +x /app/app.py

USER $USERNAME
WORKDIR /app
ENV PATH="${PATH}:/app/.local/bin"
CMD ["./app.py"]
