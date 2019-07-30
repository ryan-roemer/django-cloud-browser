ARG PYTHON_VERSION=3.7
FROM python:${PYTHON_VERSION}

RUN useradd -ms /bin/sh cloudbrowser

WORKDIR /app

COPY . .

RUN pip install .[test] --no-cache-dir

USER cloudbrowser

ENV HOST="0.0.0.0"
ENV PORT="8000"

ENTRYPOINT ["invoke"]
CMD ["run-server"]
