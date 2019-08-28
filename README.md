# Code Review Graph Data

Extracts post and link information from a Stack Exchange site for plotting using [Gephi](https://gephi.org/).

# Installation

```bash
$ git pull https://github.com/Peilonrayz/stack_exchange_graph_data.git
$ pip install .[dev]
```

**Note**, if you have got mam working and need to reinstall then use the following instead:

```bash
$ python setup.py sdist
$ pip install ./dist/stack_exchange_graph_data-0.0.1.tar.gz[dev]
```

# Testing

All tests use are run via tox. This includes running static analysis tools, unit tests and generating documentation.

```bash
$ tox
```
