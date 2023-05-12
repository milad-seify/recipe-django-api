FROM python:alpine3.18
LABEL maintainer="miladsey"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    rm -rf /tmp && \
    adduser -D -H  djangomilad





ENV PATH="/py/bin:$PATH"

USER djangomilad
