"""Coroutines for converting from source data to internal data."""

from typing import Dict, Generator, List, Optional

import docutils.core
from bs4 import BeautifulSoup

from ..helpers import xref
from ..helpers.coroutines import coroutine
from ..segd import graph, models


@coroutine
def load_posts(target: Generator) -> Generator:
    """Read posts from external format into internal format."""
    post_tags: Dict[str, List[str]] = {}
    while True:
        post = yield
        if post.attrib["PostTypeId"] not in {"1", "2"}:
            pass

        post_id = post.attrib["Id"]
        parent_id: Optional[int]
        try:
            parent_id = int(post.get("ParentId"))
        except (TypeError, ValueError):
            parent_id = None

        body = BeautifulSoup(post.attrib["Body"], features="html.parser")
        if "Tags" in post.attrib:
            post_tags[post_id] = tags = post.attrib["Tags"].strip("><").split("><")
        else:
            tags = post_tags.get(post.attrib.get("ParentId"))

        target.send(
            models.Post(
                id=int(post_id),
                body=body,
                tags=tags,
                links=[link.get("href") for link in body.find_all("a")],
                parent_id=parent_id,
            )
        )


@coroutine
def get_post_links(link_target: Generator, node_target: Generator,) -> Generator:
    """
    Get all wanted data from posts.

    Gets all http links, and includes links from the parent post
    (question) to child posts (answer).

    Includes all questions and answers in node output.
    """
    while True:
        post = yield
        node_target.send(post)

        if post.parent_id is not None:
            link_target.send((post.id, post.parent_id, graph.LinkType.QAA))
            link_target.send((post.parent_id, post.id, graph.LinkType.QAA))

        for link in post.links:
            link_target.send((post.id, link, graph.LinkType.PL))


@coroutine
def load_comments(site_name: str, target: Generator) -> Generator:
    """Read comments from external format into internal format."""
    while True:
        comment = yield
        comment_as_html = BeautifulSoup(
            docutils.core.publish_string(
                source=comment.attrib["Text"],
                writer_name="html5",
                parser=xref.custom_parser(site_name)(),
                parser_name="md",
            ).decode("UTF-8"),
            features="html.parser",
        )
        body = comment_as_html.find("body")
        target.send(
            models.Comment(
                id=int(comment.attrib["PostId"]),
                body=body,
                links=[link.get("href") for link in body.find_all("a")],
            )
        )


@coroutine
def get_comment_links(target: Generator) -> Generator:
    """Get all wanted links in comments."""
    while True:
        comment = yield
        for link in comment.links:
            target.send((comment.id, link, graph.LinkType.CL))
