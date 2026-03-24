import os
from pathlib import Path

from dotenv import load_dotenv

from musicdl.__init__ import __version__
from musicdl.exceptions import MissingAPIError
from musicdl.filesystem import resolve_cache_directory, resolve_output_directory

load_dotenv()


class Settings:
    def __init__(self):
        # Project name
        self.project_name = "musicdl"

        # Project version
        self.project_version = __version__

        # API URL (required, with fallback)
        try:
            self.api_url = os.environ["API_URL"]
        except KeyError:
            try:
                self.api_url = os.environ["API_URL_BAK"]
            except KeyError:
                raise MissingAPIError

        # Timeout (optional, must be int)
        try:
            self.timeout = int(os.environ["TIMEOUT"])
        except KeyError, ValueError:
            self.timeout = 3

        # Quality (optional, validated)
        try:
            self.quality = os.environ["QUALITY"]
        except KeyError:
            self.quality = "LOSSLESS"

        if self.quality not in ("HI_RES_LOSSLESS", "LOSSLESS", "HIGH", "LOW"):
            self.quality = "LOSSLESS"

        # Output directory
        try:
            self.output_directory = resolve_output_directory(os.environ["OUTPUT_DIRECTORY"])
        except KeyError:
            self.output_directory = resolve_output_directory()

        # Cache directory
        try:
            self.cache_directory = resolve_cache_directory(os.environ["CACHE_DIRECTORY"])
        except KeyError:
            self.cache_directory = resolve_cache_directory()


settings = Settings()
