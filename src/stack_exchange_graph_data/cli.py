"""
Argument parser functions.

The exposed arguments are:

--help                  show this help message and exit
--no-expand-meta        don't include links that use the old domain name
                        structure
--download              redownload data, even if it exists in the cache
--min MIN               minimum sized networks to include in output
--max MAX               maximum sized networks to include in output
--output OUTPUT         output file name
--cache-dir CACHE_DIR   cache directory

"""
import argparse


def make_parser() -> argparse.ArgumentParser:
    """Make parser for CLI arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "site_name", help="name of the site you want to get data for",
    )
    parser.add_argument(
        "--no-expand-meta",
        action="store_true",
        help="don't include links that use the old domain name structure",
    )
    parser.add_argument(
        "-d",
        "--download",
        action="store_true",
        help="redownload data, even if it exists in the cache",
    )
    parser.add_argument(
        "--min",
        type=int,
        default=0,
        help="minimum sized networks to include in output",
    )
    parser.add_argument(
        "--max",
        type=int,
        default=float("inf"),
        help="maximum sized networks to include in output",
    )
    parser.add_argument(
        "-o", "--output", default="{site_name}", help="output file name",
    )
    parser.add_argument(
        "--cache-dir", default=".cache/", help="cache directory",
    )
    return parser
