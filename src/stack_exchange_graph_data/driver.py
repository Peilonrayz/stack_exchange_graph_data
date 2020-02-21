"""
Connect and run the control flow of the program.

Since all the coroutines wrapped with
:func:`stack_exchange_graph_data.helpers.coroutines.coroutine` are stand
alone coroutines. Which require the target coroutine to be passed at
creation time. This means that when we want to interact with them we
need to create the entire control flow, which we do here.

The entire control flow of the coroutines is:

.. graphviz::

    digraph G {
        file_sink_l [label="file_sink"];
        file_sink_n [label="file_sink"];

        subgraph cluster_0 {
            label="links_driver";
            color="#0074C1";

            node [color="#0074C1"];
                handle_links;
                filter_links;
                filter_duplicates;
                filter_network_size;
                sheet_prep;

            sheet_prep -> file_sink_l;
        }

        subgraph cluster_1 {
            label="nodes_driver";
            color="#FFE050";

            node [color="#FFE050"];
                handle_nodes;

            handle_nodes -> file_sink_n;
        }

        subgraph cluster_2 {
            label="navigate";
            color="#05930C";

            node [color="#05930C"];
                load_posts;
                get_post_links;
                load_comments;
                get_comment_links;
        }

        handle_links -> filter_links -> filter_duplicates
            -> filter_network_size -> sheet_prep;
        handle_links -> filter_duplicates;

        load_posts -> get_post_links -> {handle_links, handle_nodes};
        load_comments -> get_comment_links -> handle_links;
    }

"""

import argparse
import pathlib
from typing import Generator, Optional

from defusedxml import ElementTree

from .coroutines import data_sources as ds
from .coroutines import links, nodes
from .helpers import coroutines, progress
from .segd import cache, file_system, site_info


def load_xml_stream(
    file_path: pathlib.Path, progress_message: Optional[str] = None
) -> progress.ItemProgressStream:
    """Load an iterable xml file with a progress bar."""
    all_posts = ElementTree.parse(file_path).getroot()
    return progress.ItemProgressStream(
        all_posts, len(all_posts), prefix="  ", message=progress_message,
    )


def links_driver(
    arguments: argparse.Namespace, _site_info: site_info.SiteInfo,
) -> Generator:
    """Build the control flow for links."""
    links_mid = links.filter_duplicates(
        links.filter_network_size(
            arguments,
            links.sheet_prep(
                coroutines.file_sink(arguments.output + ".edges.csv", "w"),
            ),
        ),
    )
    return links.handle_links(
        links.filter_links(
            ({_site_info.domain} if arguments.no_expand_meta else _site_info.domains),
            links_mid,
        ),
        links_mid,
    )


def nodes_driver(arguments: argparse.Namespace) -> Generator:
    """Build the control flow for nodes."""
    return nodes.handle_nodes(
        coroutines.file_sink(arguments.output + ".nodes.csv", "w"),
    )


def navigate(
    _file_system: file_system.FileSystem, arguments: argparse.Namespace,
) -> None:
    """Build and navigate the coroutine control flow."""
    _site_info = _file_system.get_site_info(
        arguments.site_name, not arguments.download,
    )
    _links = links_driver(arguments, _site_info)
    coroutine_delegator = coroutines.CoroutineDelegator()
    coroutine_delegator.send_to(
        load_xml_stream(
            _file_system.get_site_file(
                _site_info, "Posts.xml", not arguments.download,
            ),
            "Extracting data from posts.",
        ),
        ds.load_posts(ds.get_post_links(_links, nodes_driver(arguments))),
    )
    coroutine_delegator.send_to(
        load_xml_stream(
            _file_system.get_site_file(_site_info, "Comments.xml",),
            "Extracting data from comments.",
        ),
        ds.load_comments(_site_info.url, ds.get_comment_links(_links)),
    )
    coroutine_delegator.run()


def main(arguments):
    file_system_ = file_system.FileSystem(
        cache.Cache(
            pathlib.Path(arguments.cache_dir),
            "https://archive.org/download/stackexchange/",
        )
    )
    navigate(file_system_, arguments)
