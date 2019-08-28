"""Expand partial xrefs."""
# nosa: pylint,mypy

from typing import List, Type

import docutils.core
import docutils.nodes
import docutils.parsers
import docutils.transforms

from recommonmark.parser import CommonMarkParser

import sphinx.addnodes

__all__ = [
    'custom_parser',
]


def custom_parser(prefix: str) -> Type[docutils.parsers.Parser]:
    """
    Markdown parser with partial xref support.

    Extends :code:`recommonmark.parser.CommonMarkParser` with to include
    the :code:`custom_parser.PendingXRefTransform` transform.

    :param prefix: Http base to prepend to partial hyperlinks.
    :return: A custom parser to parse Markdown.
    """
    class PendingXRefTransform(docutils.transforms.Transform):
        """
        Expands partial links.

        Some links are provided like :code:`[text](/a/2)``.
        This expands the link to include the basename like:

        .. :
           http://codereview.meta.stackexchange.com
        """

        default_priority = 999

        @staticmethod
        def handle_xref(
                node: sphinx.addnodes.pending_xref,
        ) -> docutils.nodes.Node:
            """Convert partial_xref to desired output."""
            referance, = node.children
            ref = node.attributes['reftarget']
            if ref != referance.attributes['refuri']:
                print(
                    'target not the same',
                    node.attributes['reftarget'],
                    referance.attributes['refuri'],
                )

            if ref.startswith('/'):
                referance['refuri'] = prefix + ref
                return referance
            # Handles 'links' like [this other thing](link)
            text, = referance.children
            if not isinstance(text, docutils.nodes.Text):
                print('Referance text is not text.')
            return docutils.nodes.Text(f'[{text.rawsource}]({ref})')

        def traverse(self, node: docutils.nodes.Node) -> None:
            """Traverse the tree updating partial_xref nodes."""
            transforms = []
            children = []
            for child in getattr(node, 'children', [])[:]:
                if isinstance(child, sphinx.addnodes.pending_xref):
                    new_child = self.handle_xref(child)
                    transforms.append((child, new_child))
                    child = new_child
                children.append(child)

            replace = getattr(node, 'replace', None)
            if replace is not None:
                for old, new in transforms:
                    replace(old, new)

            for child in children:
                self.traverse(child)

        def apply(self) -> None:
            """Docutils entry."""
            self.traverse(self.document)

    class CustomParser(CommonMarkParser):
        """Subclass of CommonMark to add XRef transform."""

        def get_transforms(self) -> List[Type[docutils.transforms.Transform]]:
            """Get transformations used for this passer."""
            return [PendingXRefTransform]

    return CustomParser
