"""
main.py

The musicdl Command Line Interface.

Usage:
uv run musicdl 123
uv run python -m musicdl 123
"""

from .cli import create_arg_parser


def main(argv: list[str] | None = None) -> int:
    """
    Run the main program.

    This function is executed when you type `musicdl` or `python -m musicdl`
    """

    parser = create_arg_parser()
    parsed_args = parser.parse_args(args=argv)
    verbosity_level = 1

    print(parsed_args.resource_id)

    if parsed_args.quiet:
        verbosity_level = 0
    elif parsed_args.verbose:
        verbosity_level = 2

    return 0
