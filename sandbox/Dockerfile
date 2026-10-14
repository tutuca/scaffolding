# The sandbox: the built wheel on a bare Debian, nothing else. Throwaway - the
# deployment is `uv tool install` on a host, no docker (docs/INFRASTRUCTURE.md).
# Context is the wheel and sandbox/requirements.txt (sandbox/Dockerfile.dockerignore).
# Two layers: the pinned dependencies, rebuilt only when the lock changes (pip's
# cache survives that), and the wheel, rebuilt on every `make package`.
# What to run is the caller's: the image is the `scaffolding` command and nothing more.
FROM python:3.14-slim

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    SCAFFOLDING_VAR_DIR=/state/var \
    SCAFFOLDING_SECRETS_DIR=/state/secrets \
    DEBUG=true

COPY sandbox/requirements.txt /tmp/
RUN --mount=type=cache,target=/root/.cache/pip pip install -r /tmp/requirements.txt
COPY dist/scaffolding-*.whl /tmp/
RUN pip install --no-cache-dir --no-deps /tmp/scaffolding-*.whl

RUN mkdir -p $SCAFFOLDING_VAR_DIR $SCAFFOLDING_SECRETS_DIR
VOLUME /state
CMD ["scaffolding"]
