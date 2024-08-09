FROM python:slim AS base

ARG CI_JOB_TOKEN

ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV PATH=$PATH:/root/.local/bin
ENV PIP_EXTRA_INDEX_URL="https://__token__:${CI_JOB_TOKEN}@gitlab.com/api/v4/groups/${CI_PROJECT_ID}/-/packages/pypi/simple"
ENV LISTEN=0.0.0.0:8000

WORKDIR /root

FROM base AS dev
COPY ./src ./src
COPY pyproject.toml ./
RUN pip install -e .[dev]
CMD ["scaffolding", "runserver", "0.0.0.0:8000"]

FROM base AS runtime
RUN pip install scaffolding
CMD ["gunicorn", "scaffolding.wsgi:application", "-w", "2", "-b", ":8000", "--capture-output"]
