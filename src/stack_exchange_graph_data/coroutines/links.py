"""Link coroutine control flow functions."""

import argparse
import collections
import urllib.parse
from typing import DefaultDict, Generator, List, Set

from ..helpers.coroutines import coroutine
from ..segd import graph


@coroutine
def handle_links(filter_: Generator, good: Generator) -> Generator:
    """Send http and id links to correct target."""
    while True:
        orig_id, link, link_type = yield
        target = filter_ if isinstance(link, str) else good
        target.send((orig_id, link, link_type))


@coroutine
def filter_links(domains: Set[str], target: Generator) -> Generator:
    """Filter links to links to posts on the provided site."""
    while True:
        orig_id, link, link_type = yield
        url = urllib.parse.urlparse(link)

        if url.netloc not in domains:
            continue

        segments: List[str] = url.path.split('/')
        list_ = segments[1] if len(segments) >= 2 else None
        post_id = segments[2] if len(segments) >= 3 else ''
        if list_ not in {'questions', 'a', 'q'}:
            continue

        if url.query:
            try:
                _, post_id = url.query.split('_', 1)
                int(post_id)
            except ValueError:
                pass

        try:
            int(post_id)
        except (ValueError, TypeError):
            continue
        target.send((orig_id, post_id, link_type))


@coroutine
def filter_duplicates(target: Generator) -> Generator:
    """Remove duplicate links from the output."""
    link_lookup: DefaultDict[int, DefaultDict[int, Set[graph.LinkType]]]
    link_lookup = collections.defaultdict(lambda: collections.defaultdict(set))
    try:
        while True:
            from_node, to_node, link_type = yield
            link_lookup[from_node][to_node].add(link_type)
    finally:
        for from_node, links_to in link_lookup.items():
            for to_node, types in links_to.items():
                target.send((
                    from_node,
                    to_node,
                    max(types, key=lambda i: i.value.weight),
                ))


@coroutine
def filter_network_size(
        arguments: argparse.Namespace,
        target: Generator,
) -> Generator:
    """
    Filter networks that aren't the wanted size.

    :param arguments: CLI parser arguments that dictate the min and max size.
    """
    graph_ = graph.Graph()
    try:
        while True:
            item = yield
            graph_.add(*item)
    finally:
        for network in graph_.get_networks():
            if not arguments.min <= len(network) <= arguments.max:
                continue
            for node in network:
                for link in node.links:
                    edge_type = link.type.value
                    target.send((
                        node.value,
                        link.target.value,
                        edge_type.weight,
                        edge_type.type,
                    ))


@coroutine
def sheet_prep(target: Generator) -> Generator:
    """Convert into the format required to be sent to disk."""
    target.send('Source;Target;Weight;Type\n')
    while True:
        edge = yield
        target.send(';'.join(map(str, edge)) + '\n')
