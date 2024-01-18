# edea python library

The core python module and CLI for the edea project.


## Installation

```
pip install edea
```

### Installing pre-release modules

```sh
pip install edea --index-url https://gitlab.com/api/v4/projects/35843774/packages/pypi/simple
```
or using poetry:
```sh
poetry source add --priority=explicit gitlab https://gitlab.com/api/v4/projects/35843774/packages/pypi/simple
poetry add --source gitlab edea
```

## Documentation
[latest docs](https://edea-dev.gitlab.io/edea/latest/)

## Running the tool

To run the tool for test & development purposes either enter a venv or use poetry to run it:

## Running the tests

The tests should run in the venv to make sure the development tools are there:

```sh
# outside the poetry environment:
poetry run pytest
# or
poetry shell
# now we're inside the venv and can run like before, but now with test coverage
pytest --cov-report term-missing --cov=edea

# it's also possible to run a single test or a test class
pytest -k test_parse
```

### Long running test

`test_parse_all` and `test_serialize_all` process a lot of KiCad files which
can take a long time. They are skipped by default if the files are not there but
you can enable them by retrieving the files.

```sh
# the files are in the kicad6-test-files git submodule, retrieve them
git submodule update --init
# we'd like to parallelize the tests using pytest-xdist to speed things up
# automatically detecting the optimal number of processes for your machine
poetry run pytest -n auto
```
