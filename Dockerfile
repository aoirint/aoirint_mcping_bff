# syntax=docker/dockerfile:1.6
FROM python:3.11

ARG DEBIAN_FRONTEND=noninteractive
ARG PIP_NO_CACHE_DIR=1
ENV PYTHONUNBUFFERED=1
ENV PATH=/code/aoirint_mcping_bff/.venv/bin:/home/user/.local/bin:${PATH}

RUN <<EOF
    set -eu

    apt-get update
    apt-get install -y \
        gosu

    apt-get clean
    rm -rf /var/lib/apt/lists/*
EOF

RUN <<EOF
    set -eu

    groupadd --non-unique --gid 1000 user
    useradd --non-unique --uid 1000 --gid 1000 --create-home user
EOF

ARG POETRY_VERSION=1.8.2
RUN <<EOF
    set -eu

    gosu user pip install "poetry==${POETRY_VERSION}"

    gosu user poetry config virtualenvs.in-project true

    mkdir -p /home/user/.cache/pypoetry/{cache,artifacts}
    chown -R "user:user" /home/user/.cache
EOF

RUN <<EOF
    set -eu

    mkdir -p /code/aoirint_mcping_bff
    chown -R "user:user" /code/aoirint_mcping_bff
EOF

WORKDIR /code/aoirint_mcping_bff
ADD --chown=1000:1000 ./pyproject.toml ./poetry.lock /code/aoirint_mcping_bff/
RUN --mount=type=cache,uid=1000,gid=1000,target=/home/user/.cache/pypoetry/cache \
    --mount=type=cache,uid=1000,gid=1000,target=/home/user/.cache/pypoetry/artifacts <<EOF
    set -eu

    gosu user poetry install --no-root --only main
EOF

ADD --chown=1000:1000 ./aoirint_mcping_bff /code/aoirint_mcping_bff/aoirint_mcping_bff
ADD --chown=1000:1000 ./README.md ./main.py /code/aoirint_mcping_bff/
RUN --mount=type=cache,uid=1000,gid=1000,target=/home/user/.cache/pypoetry/cache \
    --mount=type=cache,uid=1000,gid=1000,target=/home/user/.cache/pypoetry/artifacts <<EOF
    set -eu

    gosu user poetry install --only main
EOF

CMD [ "gosu", "user", "poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000" ]
