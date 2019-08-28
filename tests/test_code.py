import pathlib

from defusedxml import ElementTree

from stack_exchange_graph_data.segd import driver, cache


def test_site_info():
    fs = driver.FileSystem(cache.Cache(
        pathlib.Path('.cache/'),
        'https://archive.org/download/stackexchange/'
    ))
    with fs.get_sites() as f:
        invalid_sites = []
        for site in ElementTree.parse(f).getroot():
            s = driver.SiteInfo(site.attrib['Url'])
            if s.domain != s._gen_domain():
                invalid_sites.append(s.domain)
        assert invalid_sites == []
