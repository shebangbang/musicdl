"""
main.py

The musicdl Command Line Interface.

Usage:
uv run musicdl 123
uv run python -m musicdl 123
"""

import logging

from musicdl.api import APIClient
from musicdl.cli import create_arg_parser
from musicdl.config import settings
from musicdl.downloader import Downloader
from musicdl.exceptions import APIError, DownloaderError
from musicdl.metadata import write_flac_metadata
from musicdl.naming import generate_filename

logger = logging.getLogger(__name__)


def main(argv: list[str] | None = None) -> int:
    """
    Run the main program.

    This function is executed when you type `musicdl` or `python -m musicdl`
    """

    parser = create_arg_parser()
    parsed_args = parser.parse_args(args=argv)

    if parsed_args.quiet:
        verbosity_level = logging.ERROR
    elif parsed_args.verbose:
        verbosity_level = logging.DEBUG
    else:
        verbosity_level = logging.INFO
    logging.getLogger().setLevel(verbosity_level)

    api_client = APIClient(settings.api_url)

    downloader = Downloader(settings.output_directory)

    try:
        if parsed_args.resource_type == "track":
            # API
            track = api_client.fetch_track_info(parsed_args.resource_id)

            # Downloader
            # TODO: Check availability of quality
            file_name, file_extension = generate_filename(track)
            logging.info(f"Downloading {file_name}")
            track_location, track_size = downloader.download(file_name, track.download_url)
            logging.info(f"{file_name} downloaded")

            logging.info("Downloading cover")
            cover_location, cover_size = downloader.download("cover.jpg", track.cover_url)
            logging.info("Download complete")

            # Tagging
            logging.info("Attempting to tag track")
            write_flac_metadata(track_location, cover_location, track)
            logging.info("Tagging complete")

    except (APIError, DownloaderError) as e:
        if verbosity_level > 0:
            logger.error(e)
            print(e)
        return 1

    return 0
