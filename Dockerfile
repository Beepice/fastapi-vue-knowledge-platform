FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

EXPOSE 8000
WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat-openbsd && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY poetry.lock pyproject.toml ./
RUN pip install --upgrade pip
RUN pip install "poetry>=2.4.1"
RUN poetry config virtualenvs.in-project true
RUN poetry install --no-root

COPY . ./

CMD /app/.venv/bin/alembic upgrade head && \
    /app/.venv/bin/uvicorn --host=0.0.0.0 app.main:app
