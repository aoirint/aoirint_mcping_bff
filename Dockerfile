# syntax=docker/dockerfile:1.4
FROM python:3.10

RUN <<EOF
    apt-get update
    apt-get install -y \
        gosu
    apt-get clean
    rm -rf /var/lib/apt/lists/*
EOF

RUN <<EOF
    groupadd -o -g 1000 user
    useradd -m -o -u 1000 -g user user
EOF

ENV PATH=/home/user/.local/bin:${PATH}

WORKDIR /work
ADD ./requirements.txt /work/
RUN <<EOF
    gosu user pip3 install -r /work/requirements.txt
EOF

ADD main.py /work/

CMD [ "gosu", "user", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000" ]
