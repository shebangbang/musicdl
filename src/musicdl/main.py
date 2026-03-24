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
from musicdl.downloader import Downloader
from musicdl.exceptions import APIError, DownloaderError
from musicdl.util import resolve_output_directory


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
        if not os.environ["QUALITY"]:
            print("Defaulting to LOSSLESS quality.")

    api_client = APIClient.from_env()

    output_dir = resolve_output_directory()
    print(output_dir)
    downloader = Downloader(output_dir)

    try:
        if parsed_args.resource_type == "track":
            track = api_client.fetch_track_info(parsed_args.resource_id)
            print(track.artist)

            # downloader
            track_file, track_size = downloader.download(
                track.title, track.download_url
            )
    except (APIError, DownloaderError) as e:
        if verbosity_level > 0:
            print(e)
        return 1

    return 0
