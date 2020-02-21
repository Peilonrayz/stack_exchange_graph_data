"""SEGD cache endpoints."""

import pathlib

from ..helpers import cache
from . import site_info


class Cache:
    """SEGD Cache object."""

    def __init__(self, cache_dir: pathlib.Path, archive: str) -> None:
        """Initialize Cache."""
        self.archive = archive
        self.cache = cache.Cache(cache_dir)

    @property
    def sites(self) -> cache.FileCache:
        """
        Endpoint for the :code:`Sites.xml` file.

        This contains metadata about all sites. This allows us to use a
        short hand name to get the required site domain. It also allows
        us to easily see if the site requested even exists.
        """
        return self.cache.file("Sites.xml", self.archive + "Sites.xml")

    def site_archive(self, site: site_info.SiteInfo) -> cache.FileCache:
        """
        Endpoint for the site's 7z archive.

        :param site: The site info object of the wanted archive.
        """
        return self.cache.file(f"{site.domain}.7z", self.archive + f"{site.domain}.7z",)

    def site_file(
        self, site: site_info.SiteInfo, file_path: str,
    ) -> cache.Archive7zCache:
        """
        Endpoint for the site's unarchived data.

        These are files such as :code:`Comments.xml` or :code:`Posts.xml`.
        These contain the actual data from the Stack Exchange data dump.

        :param site: The site info object of the wanted data dump data.
        :param file_path: The unarchived file wanted - :code:`Comments.xml`.
        """
        return self.cache.archive_7z(
            pathlib.Path(site.name, file_path), self.site_archive(site),
        )
