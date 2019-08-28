"""Node control flow coroutines."""

import collections
from typing import Generator

from ..helpers.coroutines import coroutine


@coroutine
def handle_nodes(target: Generator) -> Generator:
    """Send all posts to the output, with information about the top 36 tags."""
    nodes = []
    try:
        while True:
            nodes.append((yield))
    finally:
        tags = collections.Counter(
            tag
            for node in nodes
            for tag in node.tags or []
        )
        top_tags = [t for t, _ in tags.most_common(36)]
        target.send(';'.join(['Id'] + top_tags) + '\n')
        for node in nodes:
            target.send(
                ';'.join(
                    [str(node.id)]
                    + [
                        str(tag in (node.tags or []))
                        for tag in top_tags
                    ],
                ) + '\n',
            )
