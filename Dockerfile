# syntax=docker/dockerfile:1.6
FROM python:3.11

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

ENV PATH=/home/user/.local/bin:${PATH}

WORKDIR /work
ADD ./requirements.txt /work/
RUN <<EOF
    set -eu

    gosu user pip3 install -r /work/requirements.txt
EOF

ADD main.py /work/

CMD [ "gosu", "user", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000" ]
