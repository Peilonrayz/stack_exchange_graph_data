"""Holds the driving segments of the program."""

import pathlib
from typing import IO, Any

from defusedxml import ElementTree

from . import cache, site_info


class FileSystem:
    """File System interactions."""

    def __init__(self, segd_cache: cache.Cache) -> None:
        """Initialize FileSystem."""
        self.cache = segd_cache

    def get_sites(self, use_cache: bool = True) -> IO[bytes]:
        """
        Open the :code:`Sites.xml` file from cache.

        :param use_cache: Set to false to force redownload of data.
        :return: The :code:`Sites.xml` file in binary read mode.
        """
        return self.cache.sites.ensure(use_cache).open("rb")

    def get_site_archive(
        self, site: site_info.SiteInfo, use_cache: bool = True,
    ) -> pathlib.Path:
        """
        Ensure the site's 7z archive is in cache.

        :param site: The site info object of the wanted archive.
        :param use_cache: Set to false to force redownload of data.
        :return: The location of the cached 7z archive.
        """
        return self.cache.site_archive(site).ensure(use_cache)

    def get_site_file(
        self, site: site_info.SiteInfo, file_path: str, use_cache: bool = True,
    ) -> pathlib.Path:
        """
        Get a data file from the site's data dump.

        :param site: The site info object of the wanted data dump.
        :param use_cache: Set to false to force redownload of data.
        :return: The location fo the cached data dump file.
        """
        return self.cache.site_file(site, file_path).ensure(use_cache)

    def _get_site_info(self, site_name: str, use_cache: bool) -> Any:
        """
        Filter sites to just the wanted site.

        :param site_name: Name of site to get data for.
        :param use_cache: Set to false to force redownload of data.
        :return: Raw site data.
        """
        with self.get_sites(use_cache) as sites_path:
            for site in ElementTree.parse(sites_path).getroot():
                if any(
                    site_name == site.attrib[attr].lower()
                    for attr in ["TinyName", "Name", "LongName"]
                ):
                    return site
        raise ValueError(f"No site named {site_name}.")

    def get_site_info(
        self, site_name: str, use_cache: bool = True,
    ) -> site_info.SiteInfo:
        """
        Get site information for the provided site.

        :param site_name: Name of site to get data for.
        :param use_cache: Set to false to force redownload of data.
        :return: Object containing site information.
        """
        _site_info = self._get_site_info(site_name, use_cache)
        return site_info.SiteInfo(_site_info.attrib["Url"])
