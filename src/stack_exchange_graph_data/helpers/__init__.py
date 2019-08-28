"""
Helper modules.

These should be stand alone modules that could reasonably be their own
PyPI package. This comes with two benefits:

1. The library is void of any business data, which makes it easier to
   understand.
2. It means that it is decoupled making it easy to reuse the code in
   different sections of the code. An example is the
   :mod:`stack_exchange_graph_data.helpers.progress` module. Which is
   easily used in both :func:`stack_exchange_graph_data.helpers.curl.curl`
   and :func:`stack_exchange_graph_data.driver.load_xml_stream`. Since
   it wraps a stream it's easily transferable to any Python loop, and
   due to lacking business logic means there's no monkey patching.
"""
