"""Display progress of a stream."""

import time
import warnings
from typing import Callable, Generic, Iterator, Optional, Tuple, TypeVar

from .si import Magnitude, display

# nosa(1): pylint[:Class name "T" doesn't conform to PascalCase naming style]
T = TypeVar("T")


# nosa(1): pylint[:Too many instance attributes]
class BaseProgressStream(Generic[T]):
    """Display the progress of a stream."""

    # nosa(1): pylint[:Too many arguments]
    def __init__(
        self,
        stream: Iterator[T],
        size: Optional[int],
        si: Callable[[int], Tuple[int, str]],
        progress: Callable[[T], int],
        width: int = 20,
        prefix: str = "",
        start: int = 0,
        message: Optional[str] = None,
    ):
        """Initialize BaseProgressStream."""
        self.stream = stream
        self.size = size
        self.width = width
        self.progress_bar = "=" * (width - 1) + ">"
        self.prefix = prefix
        self.to_readable = si
        self.progress_fn = progress
        self._start = start
        self.message = message

    def _get_progress(self, current: int) -> str:
        """
        Get the progress of the stream.

        :param current: Current progress - not in percentage.
        :return: Progress bar and file size.
        """
        if not self.size:
            return ""
        amount = self.width * current // self.size
        progress = self.progress_bar[-amount:] if amount else ""
        disp_size = display(self.to_readable(self.size))
        return f"[{progress:<{self.width}}] {disp_size} "

    def __iter__(self) -> Iterator[T]:
        """
        Echo the stream, and update progress.

        Catches all warnings raised whilst processing the stream to be
        displayed afterwards. This keeps the UI tidy and prevents the
        progress bar traveling over multiple lines.

        :return: An echo of the input stream.
        """
        with warnings.catch_warnings(record=True) as warnings_:
            current = self._start
            if self.message:
                print(self.message)
            start = time.clock()
            for chunk in self.stream:
                current += self.progress_fn(chunk)
                progress = self._get_progress(current)
                rate = current // max(int(time.clock() - start), 1)
                disp_rate = display(self.to_readable(rate))
                print(
                    f"\r{self.prefix}{progress}{disp_rate}/s", end="", flush=True,
                )
                yield chunk
            print()
        for warning in warnings_:
            warnings.showwarning(
                warning.message, warning.category, warning.filename, warning.lineno,
            )


class DataProgressStream(BaseProgressStream[T]):
    """Display progress of a data stream."""

    def __init__(
        self,
        stream: Iterator[T],
        size: Optional[int],
        width: int = 20,
        prefix: str = "",
        message: Optional[str] = None,
    ):
        """Initialize DataProgressStream."""
        super().__init__(
            stream, size, Magnitude.ibyte, len, width, prefix, 0, message,
        )


class ItemProgressStream(BaseProgressStream[T]):
    """Display progress of an item stream."""

    def __init__(
        self,
        stream: Iterator[T],
        size: Optional[int],
        width: int = 20,
        prefix: str = "",
        message: Optional[str] = None,
    ):
        """Initialize ItemProgressStream."""
        super().__init__(
            stream, size, Magnitude.number, lambda _: 1, width, prefix, 1, message,
        )
