"""
Extract data from Stack Exchange archives for analysis.

Stack Exchange Graph Data generates the data needed to plot graphs in
`Gephi <https://gephi.org/>`_ to analise how interconnected posts are.
The aim is to find questions that require tags, or that should have
additional references. Improving the latter will improve the ability to
find the former.

Currently with most meta posts being in graphs of 10 or less it shows to
me that we need more references between our meta posts.

SEGD is a bit overkill in what it does and so here's a short rundown on
what it does:

1. Download all site metadata from the
   `archive <https://archive.org/download/stackexchange/>`_.
2. Download the data for the site that we have filtered to get.
3. Extract the data from the 7z archive we got in (2).
4. Extract all links between posts on that site. If you download main
   site data then it will only find the connections between posts on
   main. Where if a meta site is specified then it will limit it to meta.

   It extracts comments from posts and comments giving them different
   weightings on the exported data.

   :Q&A:
        3. Questions have the highest weighting at 3. This is because
           an answer directly relates to the question.

   :Post Link:
        2. Post links have the second highest weight as they provide
           evidence from other meta posts. It doesn't have the same weight
           as Q&As as the post may be incorrect or discouraged. And so
           whilst the links are still valid, they should be taken with a
           grain of salt.

   :Comment Links:
        1. Comment links have the lowest weight as whilst they are
           normally used to provide links to similar post, sometimes
           they're used for humor or other things that may reduce the
           validity of the connection with regard to what SEGD is try
           to achieve.

5. Once all the links have been accumulated, they are exported to the
   output file for use in Gephi.
6. We extract the tag information from each post so that we can observe
   the connections of each tag in the graph.
7. All node data is extracted to a separate output file.

Below shows how SEGD interacts with all the different modules and
packages within it. The different colours show which package they're in.

:Black:
    :mod:`stack_exchange_graph_data`

:Green:
    :mod:`stack_exchange_graph_data.coroutines`

:Yellow:
    :mod:`stack_exchange_graph_data.helpers`

:Blue:
    :mod:`stack_exchange_graph_data.segd`

.. graphviz::

    digraph G {
        rankdir=LR;
        "__main__";
        cli;
        driver;

        node [color="#05930C"];
            data_sources;
            links;
            nodes;

        node [color="#FFE050"];
            h_cache [label="helpers.cache"];
            coroutines;
            curl;
            progress;
            si;
            xref;

        node [color="#0074C1"];
            s_cache [label="segd.cache"];
            file_system;
            "graph";
            models;
            site_info;


        "__main__" -> {cli, driver};
        driver -> {
          data_sources,
          links,
          nodes,
          file_system,
          site_info,
          coroutines,
          progress
        };

        data_sources -> {models, "graph", xref, coroutines};
        links -> {"graph", coroutines};
        nodes -> coroutines;

        s_cache -> {site_info, h_cache};
        file_system -> {s_cache, site_info};

        h_cache -> {curl, si};
        curl -> progress;
        progress -> si;
    }

As can be seen the program is somewhat split. Half the libraries are
only involved in the iterator side of the program, where the other half
are only involved in the coroutine side of the program.
"""
