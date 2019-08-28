"""Stack Exchange site information."""

# nosa: pylint

from typing import List, Set, Tuple


class SiteInfo:
    """Site information object."""

    url: str
    domain: str
    domains: Set[str]

    name: str
    main_name: str
    tld: str
    is_stackexchange: bool
    is_meta: bool

    def __init__(self, domain: str) -> None:
        """Initialize SiteInfo."""
        domain = domain.split('/')[2]
        self.domain = domain
        self.url = 'https://' + domain
        (
            self.main_name,
            self.tld,
            self.is_stackexchange,
            self.is_meta,
            self._url_form,
        ) = self._split_domain(domain)
        self.domains = {
            self._gen_domain(False),
            self._gen_domain(True),
        }
        self.name = ('meta.' if self.is_meta else '') + self.main_name

    def _get_meta(self, segments: List[str]) -> Tuple[bool, bool]:
        """
        Determine if domain is a meta site.

        :param segments: Unknown domain name segments.
        :return: - If the site is a meta site.
                 - The form the URL is in.
        """
        is_meta = 'meta' in segments
        url_form = True
        if is_meta:
            url_form = not segments.index('meta')
            segments.remove('meta')
        return is_meta, url_form

    def _split_domain(self, domain: str) -> Tuple[str, str, bool, bool, bool]:
        """
        Split domain into reusable segments.

        :param domain: The domain of the site.
        :return: All information extractable from the domain.
        """
        *segments, hostname, tld = domain.split('.')
        segments = list(segments)
        is_stackexchange = hostname == 'stackexchange'
        url_form = True
        if not is_stackexchange:
            is_meta, _ = self._get_meta(segments)
        else:
            is_meta, url_form = self._get_meta(segments)
            if segments:
                hostname = segments.pop(0)
            else:
                hostname = 'meta'
        return (
            '.'.join(segments + [hostname]),
            tld,
            is_stackexchange,
            is_meta,
            url_form,
        )

    def _gen_domain(self, old_meta: bool = False) -> str:
        """
        Generate domain for the site.

        :param old_meta: This determines if we should use the alternate
                         URL form for the output.
        :return: The site's domain in the wanted format.
        """
        _url_form = not self._url_form if old_meta else self._url_form
        name = (
            self.main_name
            if not self.is_meta or self.main_name == 'meta' else
            f'meta.{self.main_name}'
            if _url_form else
            f'{self.main_name}.meta'
        )
        if self.is_stackexchange:
            name += '.stackexchange'
        return f'{name}.{self.tld}'
