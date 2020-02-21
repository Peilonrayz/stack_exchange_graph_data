"""
Simple file cache.

Exposes two forms of cache:

1. A file that is downloaded from a website.
2. A 7z archive cache - files that are extracted from a 7z archive.
"""

import pathlib

# nosa(1): pylint,mypy
import py7zlib

from . import curl, si


class CacheMethod:
    """Base cache object."""

    def __init__(self, cache_path: pathlib.Path) -> None:
        """Initialize CacheMethod."""
        self.cache_path = cache_path

    def _is_cached(self, use_cache: bool) -> bool:
        """
        Check if the target exist in the cache.

        :param use_cache: Set to false to force redownload the data.
        :return: True if we should use the cache.
        """
        return use_cache and self.cache_path.exists()

    def ensure(self, use_cache: bool = True) -> pathlib.Path:
        """
        Ensure target file exists.

        This should be overwritten in child classes.

        :param use_cache: Set to false to force redownload the data.
        :return: Location of file.
        """
        raise NotImplementedError("Should be overwritten in subclass.")


class FileCache(CacheMethod):
    """Exposes a cache that allows downloading files."""

    def __init__(self, cache_path: pathlib.Path, url: str) -> None:
        """Initialize FileCache."""
        super().__init__(cache_path)
        self.url = url

    def ensure(self, use_cache: bool = True) -> pathlib.Path:
        """
        Ensure target file exists.

        This curls the file from the web to cache, providing a progress
        bar whilst downloading.

        :param use_cache: Set to false to force redownload the data.
        :return: Location of file.
        """
        if not self._is_cached(use_cache):
            curl.curl(self.cache_path, self.url)
        return self.cache_path


class Archive7zCache(CacheMethod):
    """Exposes a cache that allows unzipping 7z archives."""

    def __init__(self, cache_path: pathlib.Path, archive_cache: CacheMethod,) -> None:
        """Initialize Archive7zCache."""
        super().__init__(cache_path)
        self.archive_cache = archive_cache

    def ensure(self, use_cache: bool = True) -> pathlib.Path:
        """
        Ensure target file exists.

        Unzips the 7z archive showing the name and size of each file
        being extracted.

        :param use_cache: Set to false to force reunarchiving of the data.
        :return: Location of file.
        """
        if not self._is_cached(use_cache):
            with self.archive_cache.ensure(use_cache).open("rb") as input_file:
                print(f"Unziping: {input_file.name}")
                archive = py7zlib.Archive7z(input_file)
                directory = self.cache_path.parent
                directory.mkdir(parents=True, exist_ok=True)
                for name in archive.getnames():
                    output = directory / name
                    member = archive.getmember(name)
                    size = si.display(si.Magnitude.ibyte(member.size))
                    print(f"  Unpacking[{size}] {name}")
                    with output.open("wb") as output_file:
                        output_file.write(archive.getmember(name).read())
        return self.cache_path


class Cache:
    """Interface to make cache instances."""

    def __init__(self, cache_dir: pathlib.Path) -> None:
        """Initialize Cache."""
        self.cache_dir = cache_dir

    def file(self, cache_path: str, url: str) -> FileCache:
        """
        Get a file cache endpoint.

        :param cache_path: Location of file relative to the cache directory.
        :param url: URL location of the file to download from if not cached.
        :return: A file cache endpoint.
        """
        return FileCache(self.cache_dir / cache_path, url)

    def archive_7z(
        self, cache_path: pathlib.Path, archive_cache: CacheMethod,
    ) -> Archive7zCache:
        """
        Get an archive cache endpoint.

        :param cache_path: Location of file relative to the cache directory.
        :param archive_cache: A cache endpoint to get the 7z archive from.
        :return: An archive cache endpoint.
        """
        return Archive7zCache(self.cache_dir / cache_path, archive_cache)
