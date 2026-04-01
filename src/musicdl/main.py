"""
main.py

The musicdl Command Line Interface.

Usage:
uv run musicdl 123
uv run python -m musicdl 123
"""

import logging
from pathlib import Path

from musicdl.api import APIClient
from musicdl.cli import create_arg_parser
from musicdl.config import settings
from musicdl.downloader import Downloader
from musicdl.exceptions import APIError, DownloaderError, DownloadFailureError
from musicdl.filesystem import resolve_output_directory
from musicdl.metadata import write_flac_metadata, write_mp3_metadata
from musicdl.models import Track
from musicdl.naming import generate_destination_path, generate_file_name
from musicdl.organizer import move_to_library

logger = logging.getLogger(__name__)


def _process_track(track: Track, downloader: Downloader) -> Path:
    # Downloader
    file_name, file_extension = generate_file_name(track)
    track_destination_path, cover_destination_path = generate_destination_path(track)
    expected_track_location = track_destination_path / file_name
    expected_cover_location = cover_destination_path / "cover.jpg"

    if expected_track_location.exists():
        logger.info("File already exists; skipping download")
        track_location = expected_track_location
    else:
        logger.info(f"Downloading {file_name}")
        track_location = downloader.download(file_name, track.download_url)
        logger.info(f"{file_name} downloaded")

        if expected_cover_location.exists():
            logger.info("Cover already exists; skipping download")
            cover_location = expected_cover_location
        else:
            logger.info("Downloading cover")
            cover_location = downloader.download("cover.jpg", track.cover_url)
            logger.info("Download complete")

        # Tagging
        logger.info("Attempting to tag track")
        if file_extension == "flac":
            write_flac_metadata(track_location, cover_location, track)
        elif file_extension == "mp3":
            write_mp3_metadata(track_location, cover_location, track)
        logger.info("Tagging complete")

        # Moving
        logger.info("Creating and moving to destination")
        track_location, cover_location = move_to_library(
            track, expected_track_location, expected_cover_location, file_name
        )
        logger.info("Moved to destination")

    return track_location


def main(argv: list[str] | None = None) -> int:
    """
    Run the main program.

    This function is executed when you type `musicdl` or `python -m musicdl`
    """

    parser = create_arg_parser()
    parsed_args = parser.parse_args(args=argv)

    # Argument override
    if parsed_args.folder:
        settings.output_directory = resolve_output_directory(parsed_args.folder)

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
        if parsed_args.action == "download":
            if parsed_args.resource_type == "track":
                track = api_client.fetch_track_info(parsed_args.resource_id_query)
                final_track_location = _process_track(track, downloader)
                logger.info(f"Track in {final_track_location}")
            elif parsed_args.resource_type == "album":
                album = api_client.fetch_album_info(parsed_args.resource_id_query)
                final_track_locations = []
                for track in album:
                    try:
                        final_track_locations.append(_process_track(track, downloader))
                    except DownloadFailureError:
                        logger.error(f"Failed to download {track.title}")
                        continue
            elif parsed_args.resource_type == "playlist":
                playlist = api_client.fetch_playlist_info(parsed_args.resource_id_query)
                final_track_locations = []
                for track in playlist:
                    try:
                        final_track_locations.append(_process_track(track, downloader))
                    except DownloadFailureError:
                        logger.error(f"Failed to download {track.title}")
                        continue
        elif parsed_args.action == "search":
            results = []
            print("Top search results:")
            if parsed_args.resource_type == "track":
                results = api_client.fetch_track_search_results(parsed_args.resource_id_query)
                for result in results:
                    print(f"{result['id']} - {result['title']} - {result['album']['title']}")
            elif parsed_args.resource_type == "album":
                results = api_client.fetch_album_search_results(parsed_args.resource_id_query)
                for result in results:
                    print(f"{result['id']} - {result['title']} - {result['artists'][0]['name']}")
            else:
                logger.error(f"Invalid argument {parsed_args.resource_type}")

    except (APIError, DownloaderError) as e:
        if verbosity_level > 0:
            logger.error(e)
        return 1

    return 0
