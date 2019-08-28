"""
Business logic for getting and extracting Stack Exchange information.

This package contains code that contains business logic rather than code
that is reasonably generic. Code that could reasonably be it's own PyPI
package is stored in the :ref:`Helpers` package. The benefits for this
approach are described in the :ref:`Helpers` section.

This code also doesn't include any :ref:`Coroutines`, this is as coroutines
have a very different design to normal code. Keeping them separate
should help reduced confusion, this is as you can enter either package
with one design mentality and not have to change their thought process at
random points in the package.

An example of the difference is :mod:`stack_exchange_graph_data.segd.cache`
which utilizes :mod:`stack_exchange_graph_data.helpers.cache`. The
latter exposes a simple reusable interface, where the former uses that
interface to build the bespoke endpoints for SEGD.
"""
