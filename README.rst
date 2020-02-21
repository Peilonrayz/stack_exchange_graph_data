Stack Exchange Graph Data
=========================

.. image:: https://travis-ci.com/Peilonrayz/stack_exchange_graph_data.svg?branch=master
   :target: https://travis-ci.com/Peilonrayz/stack_exchange_graph_data
   :alt: Build Status

About
-----

Extracts post and link information from a Stack Exchange site for plotting using `Gephi <https://gephi.org/>`_.

Installation
------------

.. code:: shell

   $ python -m pip install stack_exchange_graph_data

Documentation
-------------

Documentation is available `via GitHub <https://peilonrayz.github.io/stack_exchange_graph_data/>`_.

Testing
-------

To run all tests run ``nox``. No venv is needed; nox makes all of them for us.

.. code:: shell

   $ python -m pip install --user nox
   $ git clone https://peilonrayz.github.io/stack_exchange_graph_data/
   $ cd stack_exchange_graph_data
   stack_exchange_graph_data $ nox

License
-------

Stack Exchange Graph Data is available under the MIT license.
