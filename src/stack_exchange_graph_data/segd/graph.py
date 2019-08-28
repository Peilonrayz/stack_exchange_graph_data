"""Graph mutations."""

import collections
import dataclasses
import enum
from typing import Dict, List, Set

__all__ = [
    'LinkType',
    'Node',
    'find_graph_nodes',
]

LinkValue = collections.namedtuple('LinkValue', 'name weight type')


class LinkType(enum.Enum):
    """Graph link types."""

    QAA = LinkValue('Question & Answer', 3, 'Directed')
    PL = LinkValue('Post Link', 2, 'Directed')
    CL = LinkValue('Comment Link', 1, 'Directed')


@dataclasses.dataclass
class Node:
    """Graph Node."""

    value: int
    links: 'List[Edge]'
    inv_links: 'List[Node]'


@dataclasses.dataclass
class Edge:
    target: Node
    type: LinkType


def find_graph_nodes(node: Node) -> Set[int]:
    """
    Find all the nodes in a subgraph.

    :param node: Start node to find subgraph.
    :return: Collection on node names in the subgraph.
    """
    visited: Set[int] = set()
    stack = [node]
    while stack:
        node = stack.pop()
        if node.value in visited:
            continue
        visited.add(node.value)
        stack.extend([e.target for e in node.links])
        stack.extend(node.inv_links)
    return visited


class Graph:
    _nodes: Dict[int, Node]

    def __init__(self) -> None:
        self._nodes = {}

    def add(self, source: int, destination: int, link_type: LinkType) -> None:
        src = self._nodes.setdefault(source, Node(source, [], []))
        dest = self._nodes.setdefault(destination, Node(destination, [], []))
        src.links.append(Edge(dest, link_type))
        dest.inv_links.append(src)

    def get_networks(self) -> List[List[Node]]:
        networks: List[Set[int]] = []
        visited: Set[int] = set()
        for key, node in self._nodes.items():
            if key in visited:
                continue

            network = find_graph_nodes(node)
            visited |= network
            networks.append(network)

        return [
            [self._nodes[g] for g in network]
            for network in networks
        ]
