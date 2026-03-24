from pathlib import Path

import requests

from musicdl.config import settings
from musicdl.exceptions import (
    DownloadFailureError,
    SizeMismatchError,
)
from musicdl.filesystem import SimpleFileLock

CHUNK_SIZE = 64 * 1024  # 64KB
LOCK_NAME = ".musicdl.lock"


class Downloader:
    def __init__(self, output_directory: Path):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Connection": "keep-alive",
        })
        self.output_directory = output_directory
        self.output_directory.mkdir(parents=True, exist_ok=True)
        self.lock_file = self.output_directory / LOCK_NAME

    def download(self, file_name: str, url: str) -> tuple[Path, int]:
        """
        Function that downloads the file in chunks.

        Returns:
            Path object pointing to downloaded file, and the file size.
        """
        with SimpleFileLock(self.lock_file):
            try:
                # Obtain output path and check if already present
                output_path = self.output_directory / file_name
                if output_path.exists():
                    return output_path, output_path.stat().st_size
                temporary_file = output_path.with_suffix(output_path.suffix + ".part")

                # Check if file already exists
                current_size = temporary_file.stat().st_size if temporary_file.exists() else 0
                headers = {}
                if current_size > 0:
                    headers["Range"] = f"bytes={current_size}-"

                # TODO: Obtain timeout from env
                with self.session.get(url, timeout=settings.timeout, stream=True, headers=headers) as track:
                    # Obtain file size
                    content_length = track.headers.get("Content-Length")
                    final_size = int(content_length) if content_length else 0

                    # Restart download in case resuming is not possible
                    if track.status_code == 200 and current_size > 0:
                        # TODO: Figure out how to log restart
                        current_size = 0
                        temporary_file.unlink(missing_ok=True)
                    elif track.status_code == 206:
                        final_size += current_size
                    track.raise_for_status()

                    # Download
                    mode = "ab" if current_size > 0 else "wb"
                    with temporary_file.open(mode) as file_handle:
                        for chunk in track.iter_content(chunk_size=CHUNK_SIZE):
                            if chunk:
                                file_handle.write(chunk)
                                current_size += len(chunk)

                    # Validate if Content-Length obtained from header
                    if final_size and current_size != final_size:
                        raise SizeMismatchError(file_name)

                    # Rename file
                    temporary_file.replace(output_path)
            except requests.exceptions.HTTPError, requests.exceptions.ConnectionError, requests.exceptions.Timeout:
                raise DownloadFailureError(file_name)

        return output_path, current_size
