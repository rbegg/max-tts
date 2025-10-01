#
# Dockefile for piper tts container with optional added tests for dev target
#
ARG PYTHON_VERSION=3.11

FROM rhasspy/wyoming-piper AS base

# pord target is identical aa base
from base as prod

CMD ["--voice", "-en_US-lessac-medium"]

FROM base AS dev
ARG PYTHON_VERSION

WORKDIR /test

# Create a non-root user and group
RUN groupadd --gid 1000 testuser && \
    useradd --uid 1000 --gid 1000 --shell /bin/bash --create-home testuser

# Prevent tzdata from asking for input during build
ENV DEBIAN_FRONTEND=noninteractive \
    TTS_VOICE="en_US-lessac-medium"

# Install system dependencies: Python, pip
RUN apt-get update && apt-get install -y \
    python${PYTHON_VERSION} \
    python${PYTHON_VERSION}-venv \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Create a standard symlink for the python executable for robustness
RUN ln -s /usr/bin/python${PYTHON_VERSION} /usr/bin/python

# Create a virtual environment
RUN python -m venv /opt/venv

# Activate the virtual environment for subsequent RUN commands
#ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .


COPY --chown=testuser:testuser . .
RUN chmod +x ./run-tests.sh
RUN cp /run.sh ./run.sh
run chown 1000:1000 ./run.sh
run mkdir /data
run chown -R 1000:1000 /data

USER testuser

ENTRYPOINT ["/test/run-tests.sh", "all"]