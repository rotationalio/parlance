# Parlance

[![Tests](https://github.com/rotationalio/parlance/actions/workflows/tests.yaml/badge.svg)](https://github.com/rotationalio/parlance/actions/workflows/tests.yaml)
[![Containers](https://github.com/rotationalio/parlance/actions/workflows/containers.yaml/badge.svg)](https://github.com/rotationalio/parlance/actions/workflows/containers.yaml)
[![CodeQL](https://github.com/rotationalio/parlance/actions/workflows/codeql.yaml/badge.svg)](https://github.com/rotationalio/parlance/actions/workflows/codeql.yaml)

**An LLM evaluation tool that uses a model-to-model qualitative comparison metric.**

## Getting Started

For local development, copy the `.env.template` file to a `.env` file in the project root directory. Then create a local PosgreSQL database:

```
psql -c "CREATE DATABASE parlance WITH OWNER django"
```

Apply the database migrations (which you may need to do routinely as migrations change):

```
python manage.py migrate
```

Then run the local server:

```
python manage.py runserver
```

You should be able to open the web app at [localhost:8000](http://localhost:8000).