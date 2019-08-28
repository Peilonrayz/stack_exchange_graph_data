"""Copy URL."""

import os
import pathlib
from typing import Any

# nosa(1): pylint
import requests

from . import progress


def curl(
    path: pathlib.Path,
    *args: Any,
    **kwargs: Any,
) -> None:
    """
    Download file to system.

    Provides a progress bar of the file being downloaded and some
    statistics around the file and download.

    :param path: Local path to save the file to.
    :param args&kwargs: Passed to :code:`request.get`.
    """
    response = requests.get(*args, stream=True, **kwargs)
    response.raise_for_status()
    length_ = response.headers.get('content-length')
    length = int(length_) if length_ else None
    path.parent.mkdir(parents=True, exist_ok=True)

    print(f'Downloading: {response.url}')
    try:
        with path.open('wb') as output:
            for chunk in progress.DataProgressStream(
                response.iter_content(chunk_size=512),
                length,
                prefix='  ',
            ):
                output.write(chunk)
    except BaseException:
        os.remove(path)
        raise
