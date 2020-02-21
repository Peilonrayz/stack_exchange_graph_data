import pathlib

from defusedxml import ElementTree
from stack_exchange_graph_data.segd import cache, file_system, site_info


def test_site_info():
    fs = file_system.FileSystem(
        cache.Cache(
            pathlib.Path(".cache/"), "https://archive.org/download/stackexchange/"
        )
    )
    with fs.get_sites() as f:
        invalid_sites = []
        for site in ElementTree.parse(f).getroot():
            s = site_info.SiteInfo(site.attrib["Url"])
            if s.domain != s._gen_domain():
                invalid_sites.append(s.domain)
        assert invalid_sites == [
            "ja.meta.stackoverflow.com",
            "pt.meta.stackoverflow.com",
            "es.meta.stackoverflow.com",
            "ru.meta.stackoverflow.com",
        ]
