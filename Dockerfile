FROM python:3.12-alpine3.20

ENV PYTHONPATH=/src

RUN apk add --no-cache \
    wget \
    curl \
    g++ \
    gcc \
    libffi-dev \
    git \
    pkgconfig \
    make \
    cmake \
    libstdc++ \
    zlib-dev \
    && rm -rf /var/cache/apk/*

WORKDIR /src

ENV POETRY_VERSION=1.8.2
RUN pip install "poetry==$POETRY_VERSION"

COPY ./pyproject.toml /src/pyproject.toml

RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi --no-root

COPY . /src

CMD ["sh", "-c" , "uvicorn app.main:app --host 0.0.0.0 --forwarded-allow-ips '*'"]