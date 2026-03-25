import logging
import os

from dotenv import load_dotenv

from musicdl.__init__ import __version__
from musicdl.exceptions import MissingAPIError
from musicdl.filesystem import resolve_cache_directory, resolve_output_directory

load_dotenv()

logging.basicConfig(filename="musicdl.log", level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


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
                logger.debug("Falling back to backup API URL")
            except KeyError:
                raise MissingAPIError

        # Timeout (optional, must be int)
        try:
            self.timeout = int(os.environ["TIMEOUT"])
        except KeyError, ValueError:
            logger.debug("Timeout defaulting to 3")
            self.timeout = 3

        # Quality (optional, validated)
        try:
            self.quality = os.environ["QUALITY"]
        except KeyError:
            logger.debug("Quality defaulting to LOSSLESS")
            self.quality = "LOSSLESS"

        if self.quality not in ("HI_RES_LOSSLESS", "LOSSLESS", "HIGH", "LOW"):
            logger.debug("Quality defaulting to LOSSLESS")
            self.quality = "LOSSLESS"

        # Output directory
        try:
            self.output_directory = resolve_output_directory(os.environ["OUTPUT_DIRECTORY"])
        except KeyError:
            logger.debug("Output directory defaulting to user_downloads_dir")
            self.output_directory = resolve_output_directory()

        # Cache directory
        try:
            self.cache_directory = resolve_cache_directory(os.environ["CACHE_DIRECTORY"])
        except KeyError:
            logger.debug("Cache directory defaulting to user_cache_dir")
            self.cache_directory = resolve_cache_directory()


settings = Settings()
