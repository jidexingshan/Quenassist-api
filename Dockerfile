FROM --platform=linux/amd64 python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /workdir
COPY ./pyproject.toml /workdir/pyproject.toml
RUN pip3 install poetry==1.8.3
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev && rm -rf $POETRY_CACHE_DIR

COPY . /workdir
EXPOSE 8000
CMD ["quenassist", "server"]