.. image:: ./.github/assets/logo.png
|
.. image:: https://img.shields.io/badge/Python-3.12-blue
.. image:: https://img.shields.io/badge/FastAPI-0.130+-green
.. image:: https://img.shields.io/badge/Vue-3.x-brightgreen
.. image:: https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white
.. image:: https://img.shields.io/badge/License-MIT-blue


-------------

**Description**:
    Based on the fastapi-realworld-example-app(https://github.com/nsidnev/fastapi-realworld-example-app),
    This repository upgrade it to the environment of python3.12 with pydantic2. And delete all of their test works.
    Now, this is a simple personal knowledge platform built with FastAPI and Vue 3, backed by PostgreSQL. It can be deployed locally or with Docker.

Quickstart
-------------
First, run ``PostgreSQL``, set environment variables and create database in ``bash terminal``. For example using ``docker``: ::

    export POSTGRES_DB=postgres POSTGRES_PORT=5432 POSTGRES_USER=postgres POSTGRES_PASSWORD=postgres POSTGRES_HOST=localhost
    docker run --name pgdb --rm -d -p 5432:$POSTGRES_PORT -e POSTGRES_USER="$POSTGRES_USER" -e POSTGRES_PASSWORD="$POSTGRES_PASSWORD" -e POSTGRES_DB="$POSTGRES_DB" postgres

Then run the following commands to bootstrap your environment with ``poetry``: ::

    git clone https://github.com/Beepice/fastapi-vue-knowledge-platform.git
    cd fastapi-vue-knowledge-platform
    poetry install
    poetry shell

Then create ``.env`` file (or rename and modify ``.env.example``) in project root and set environment variables for application: ::

    touch .env
    echo APP_ENV=dev >> .env
    echo DATABASE_URL=postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_HOST:$POSTGRES_PORT/$POSTGRES_DB >> .env
    echo SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))") >> .env

Then create your front static resource ``dist`` in project, it is served by the fastapi as single page app: ::

    cd knowledge-base
    npm install
    npm run build
    cd ..

Then ``return to the workdir``, and to run the web application in debug use::

    alembic upgrade head
    uvicorn app.main:app --reload

Troubleshooting
----------------

**I want to deploy PostgreSQL locally on Linux (without Docker)**

The Quickstart uses a Docker container, but if you prefer a local install,
the following commands set up the default ``postgres`` user with a password
and create a dedicated database::

    sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'postgres'"
    sudo -u postgres createdb knowledge_db

Then point your ``DATABASE_URL`` to::

    DATABASE_URL=postgresql://postgres:postgres@localhost:5432/knowledge_db

.. note::
    If you run into the following error in your docker container:

       sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server: No such file or directory
       Is the server running locally and accepting
       connections on Unix domain socket "/tmp/.s.PGSQL.5432"?

    Ensure the DATABASE_URL variable is set correctly in the `.env` file.
    It is most likely caused by POSTGRES_HOST not pointing to its localhost.

       DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres

Deployment with Docker
----------------------

Before deploying with Docker, make sure the front-end has been built and the ``dist`` directory exists.

You must have ``docker`` and ``docker-compose`` tools installed to work with material in this section.
First, create ``.env`` file like in `Quickstart` section or modify ``.env.example``.
``POSTGRES_HOST`` must be specified as `db` or modified in ``docker-compose.yml`` also.
Then just run::

    docker-compose up -d db
    docker-compose up -d app

Application will be available on ``localhost:8000`` in your browser.

Web routes
----------

All backend routes are available on ``/docs`` or ``/redoc`` paths with Swagger or ReDoc.
Other routes are accepted by the front.

Project structure
-----------------

Files related to application are in the ``app`` or ``knowledge-base`` directories.
Application parts are:

::

    app
    ├── api              - web related stuff.
    │   ├── dependencies - dependencies for routes definition.
    │   ├── errors       - definition of error handlers.
    │   └── routes       - web routes.
    ├── core             - application configuration, startup events, logging.
    ├── db               - db related stuff.
    │   ├── migrations   - manually written alembic migrations.
    │   ├── repositories - all crud stuff.
    │   └── queries      - all sql crud stuff.
    ├── models           - pydantic models for this application.
    │   ├── domain       - main models that are used almost everywhere.
    │   └── schemas      - schemas for using in web routes.
    ├── resources        - strings that are used in web responses.
    ├── services         - logic that is not just crud related.
    └── main.py          - FastAPI application creation and configuration.

    knowledge-base
    ├──src               - vue related stuff
    │   ├── views       - views component for router
    │   └──  router     - views router for app
