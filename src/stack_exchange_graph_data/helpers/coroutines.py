"""
Coroutine helpers.

A lot of this module is based on the assumption that Python doesn't
seamlessly handle the destruction of coroutines when using multiplexing
or broadcasting. It also helps ease interactions when coroutines enter
closed states prematurely.
"""

import functools
import itertools
import types
from typing import (
    Any,
    Callable,
    Generator,
    Iterable,
    Iterator,
    List,
    Optional,
    Tuple,
    Union,
)

NEW_SOURCE = object()
EXIT = object()

IIter = Union[Iterator, Iterable]


class CoroutineDelegator:
    """Helper class for delegating to coroutines."""

    _queue: List[Tuple[IIter, Generator]]

    def __init__(self) -> None:
        """Initialize CoroutineDelegator."""
        self._queue = []

    def send_to(self, source: IIter, target: Generator,) -> None:
        """
        Add a source and target to send data to.

        This does not send any data into the target, to do that use the
        :meth:`CoroutineDelegator.run` function.

        :param source: Input data, can be any iterable. Each is passed
                       straight unaltered to target.
        :param target: This is the coroutine the data enters into to get
                       into the coroutine control flow.
        """
        self._queue.append((source, target))

    def _increment_coroutine_refs(self) -> None:
        """Increment the amount of sources for the coroutines."""
        for _, target in self._queue:
            if _is_magic_coroutine(target):
                target.send(NEW_SOURCE)

    def _run(self, source: IIter, target: Generator) -> Optional[Iterator]:
        item = sentinel = object()
        source_ = iter(source)
        try:
            for item in source_:
                target.send(item)
        except StopIteration:
            if item is sentinel:
                return source_
            return itertools.chain([item], source_)
        else:
            if _is_magic_coroutine(target):
                target.send(EXIT)
        return None

    def run(self) -> List[Iterator]:
        """
        Send all data into the coroutine control flow.

        :return: If a coroutine is closed prematurely the data that
                 hasn't been entered into the control flow will be
                 returned. Otherwise an empty list is.
        """
        self._increment_coroutine_refs()

        output: List[Optional[Iterator]] = [None for _ in range(len(self._queue))]
        for i, (source, target) in enumerate(self._queue):
            output[i] = self._run(source, target)
        self._queue = []
        if any(output):
            return [iter(o or []) for o in output]
        return []


def primed_coroutine(function: Callable[..., Generator]) -> Callable:
    """
    Primes a coroutine at creation.

    :param function: A coroutine function.
    :return: The coroutine function wrapped to prime the coroutine at creation.
    """
    function = types.coroutine(function)

    def inner(*args: Any, **kwargs: Any) -> Generator:
        output = function(*args, **kwargs)
        next(output)
        return output

    return inner


def _is_magic_coroutine(target: Any) -> bool:
    """
    Check if target is a magic coroutine.

    :param target: An object to check against.
    :return: If the object is a magic coroutine.
    """
    try:
        return bool(
            target and target.__qualname__.endswith("coroutine.<locals>.magic"),
        )
    except Exception:
        return False


def coroutine(function: Callable) -> Callable:
    """
    Wrap a coroutine generating function to make magic coroutines.

    A magic coroutine is wrapped in a protective coroutine that eases
    the destruction of coroutine pipelines. This is because the
    coroutine is wrapped in a 'bubble' that:

    1. Primes the coroutine when the first element of data is passed to it.
    2. Sends information about the creation and destruction of other
       coroutines in the pipeline. This allows a coroutine to destroy
       itself when all providers have exited.
    3. Handles when a coroutine is being prematurely closed, if this is
       the case all target coroutines will be notified that some data
       sources are no longer available allowing them to deallocate
       themselves if needed.
    4. Handles situations where a target coroutine has been prematurely
       closed. In such a situation the current coroutine will be closed
       and exit with a StopIteration error, as if the coroutine has been
       closed with the :code:`.close`.

    It should be noted that these coroutine pipelines should be started via the
    :class:`stack_exchange_graph_data.helpers.coroutines.CoroutineDelegator`.
    This is as it correctly initializes the entry coroutine, and handles
    when the coroutine has been prematurely closed.

    :param function: Standard coroutine generator function.
    :return: Function that generates magic coroutines.
    """
    self: Generator

    @primed_coroutine
    def magic(*args: Any, **kwargs: Any) -> Generator:
        # Get magic coroutine targets
        targets_ = itertools.chain(args, kwargs.values())
        targets = [t for t in targets_ if _is_magic_coroutine(t)]

        # Create wrapped coroutine
        wrapped = function(*args, **kwargs)

        # Broadcast the creation of a new source to the targets
        for target in targets:
            target.send(NEW_SOURCE)

        sources = 0
        generator_exit_flag = False
        generator_iteration_flag = False
        active = False
        try:
            # Main coroutine loop handles adding and removing source counters.
            while True:
                item = yield
                if item is NEW_SOURCE:
                    sources += 1
                elif item is EXIT:
                    sources -= 1
                    if not sources:
                        break
                else:
                    # Allows coroutines to be uninitialized until
                    # they're needed to be active.
                    if not active:
                        next(wrapped)
                        active = True
                    wrapped.send(item)
        # Raised when a anything above parent has been killed
        except RuntimeError:
            pass
        # Raised when a parent has been killed
        except StopIteration:
            generator_iteration_flag = True
        # Raised when this is being killed via `.close`.
        except GeneratorExit:
            generator_exit_flag = True
        finally:
            # Close the wrapped coroutine
            # This happens first, so any code in a `finally` can
            # propagate correctly
            try:
                wrapped.close()
            except RuntimeError:
                pass

            # Decrement target coroutine's source counters
            if targets and not generator_iteration_flag:
                for target in targets:
                    try:
                        for _ in range(sources):
                            target.send(EXIT)
                    except StopIteration:
                        pass

            # Coroutine must yield when it's being killed. IDK why but it does.
            # But it's illegal to yield when a GeneratorExit has been raised.
            if not generator_exit_flag:
                yield

    @functools.wraps(function)
    def inner(*args: Any, **kwargs: Any) -> Generator:
        nonlocal self
        self = magic(*args, **kwargs)
        return self

    return inner


@coroutine
def broadcast(*targets: Generator) -> Generator:
    """Broadcast items to targets."""
    while True:
        item = yield
        for target in targets:
            target.send(item)


@coroutine
def file_sink(*args: Any, **kwargs: Any) -> Generator:
    """Send all data to a file."""
    with open(*args, **kwargs) as file_obj:
        while True:
            file_obj.write((yield))
