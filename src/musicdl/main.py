"""
main.py

The musicdl Command Line Interface.

Usage:
uv run musicdl 123
uv run python -m musicdl 123
"""

import os

from dotenv import load_dotenv

from musicdl.api import APIClient
from musicdl.cli import create_arg_parser
from musicdl.exceptions import APIError


def main(argv: list[str] | None = None) -> int:
    """
    Run the main program.

    This function is executed when you type `musicdl` or `python -m musicdl`
    """

    load_dotenv()

    parser = create_arg_parser()
    parsed_args = parser.parse_args(args=argv)
    verbosity_level = 1

    print(parsed_args.resource_id)

    if parsed_args.quiet:
        verbosity_level = 0
    elif parsed_args.verbose:
        verbosity_level = 2
        if "QUALITY" not in os.environ:
            print("Defaulting to LOSSLESS quality.")

    # API
    api_client = APIClient.from_env()

    if verbosity_level == 2 and "QUALITY" not in os.environ:
        print("Defaulting to LOSSLESS quality.")

    try:
        if parsed_args.resource_type == "track":
            track = api_client.fetch_track_info(parsed_args.resource_id)
            print(track.artist)
    except APIError as e:
        if verbosity_level > 0:
            print(e)
        return 1

    return 0
