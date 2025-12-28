#
# Dockefile for piper tts container with optional added tests for dev target
#
ARG PYTHON_VERSION=3.11

FROM rhasspy/wyoming-piper AS base

USER root

RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*


# prod target is identical as base
FROM base AS prod

CMD ["--voice", "-en_US-lessac-medium"]

# dev target could enable testable env
FROM base AS dev

CMD ["--voice", "-en_US-lessac-medium"]