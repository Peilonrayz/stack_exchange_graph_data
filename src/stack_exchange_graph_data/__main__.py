"""
Extract links form SE data dumps.

SEGD exposes a commandline interface to change the functionality of the
program. These can be seen by using the :code:`--help` flag or in the
`CLI`_ section.
"""

from . import cli, driver


def main() -> None:
    """Run the program from the CLI interface."""
    arguments = cli.make_parser().parse_args()
    arguments.output = arguments.output.format(**arguments.__dict__)
    driver.main(arguments)


if __name__ == "__main__":
    main()
