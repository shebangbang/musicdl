import os
import tempfile
import threading
from pathlib import Path
from typing import Any

import requests
import validators

from musicdl.exceptions import (
    DownloadFailureError,
    InvalidURLError,
    SizeMismatchError,
)
from musicdl.util import SimpleFileLock


class Downloader:
    def __init__(self, output_dir: Path):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Connection": "keep-alive",
            }
        )
        self.output_dir = output_dir

    def download(self, track_name: str, url: str) -> tuple[Path, int]:
        """
        Function that downloads the file in chunks.

        Returns:
            Path object pointing to downloaded file and the file size.
        """
        if not validators.url(url):
            raise InvalidURLError
        # temporary_file = Path(
        #     tempfile.mkstemp(
        #         prefix="music.", suffix=".part.flac", dir=str(self.output_dir)
        #     )[1]
        # )
        actual_size = 0
        current_size = 0
        try:
            # TODO: Obtain timeout from env
            with requests.get(url, timeout=3, stream=True) as track:
                track.raise_for_status()
                final_size = int(track.headers.get("Content-Length", 0))
                file_format = track.headers.get("Content-Type", "flac").split("/")[1]

                file_name = f"{track_name}.{file_format}"
                output_path = self.output_dir / file_name
                temporary_file = output_path.with_suffix(output_path.suffix + ".part")

                with open(temporary_file, "wb") as file_handle:
                    for chunk in track.iter_content(chunk_size=128):
                        if chunk:
                            file_handle.write(chunk)
                            current_size += len(chunk)
                            break

                if final_size and current_size != final_size:
                    raise SizeMismatchError(file_name)
                os.replace(temporary_file, output_path)
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
            raise DownloadFailureError(track_name)

        return output_path, current_size
