"""
main.py

The musicdl Command Line Interface.

Usage:
uv run musicdl 123
uv run python -m musicdl 123
"""

import logging
import os

from dotenv import load_dotenv

from musicdl.api import APIClient
from musicdl.cli import create_arg_parser
from musicdl.config import settings
from musicdl.downloader import Downloader
from musicdl.exceptions import APIError, DownloaderError
from musicdl.naming import generate_filename

logger = logging.getLogger(__name__)


def main(argv: list[str] | None = None) -> int:
    """
    Run the main program.

    This function is executed when you type `musicdl` or `python -m musicdl`
    """

    parser = create_arg_parser()
    parsed_args = parser.parse_args(args=argv)

    verbosity_level = logging.INFO
    if parsed_args.quiet:
        verbosity_level = logging.ERROR
    elif parsed_args.verbose:
        verbosity_level = logging.DEBUG
    logging.basicConfig(filename="musicdl.log", level=verbosity_level)

    api_client = APIClient(settings.api_url)

    downloader = Downloader(settings.output_directory)

    try:
        if parsed_args.resource_type == "track":
            # API
            track = api_client.fetch_track_info(parsed_args.resource_id)
            print(track.artist)

            # Downloader
            # TODO: Check availability of quality
            file_name = generate_filename(track)
            track_file, track_size = downloader.download(file_name, track.download_url)
    except (APIError, DownloaderError) as e:
        if verbosity_level > 0:
            print(e)
        return 1

    return 0
