"""Common models used in control flow."""

from typing import List, NamedTuple, Optional

from bs4 import BeautifulSoup


class Comment(NamedTuple):
    """Comment data."""

    id: int
    body: str
    links: List[str]


class Post(NamedTuple):
    """Post data."""

    id: int
    body: BeautifulSoup
    links: List[str]
    tags: List[str]
    parent_id: Optional[int]
