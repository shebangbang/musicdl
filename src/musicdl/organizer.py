import os
from pathlib import Path

from musicdl.config import settings
from musicdl.models import Track


def move_to_library(
    track: Track, track_destination_path: Path, cover_destination_path: Path, file_name: str
) -> tuple[Path, Path]:
    # Create folders
    track_destination_path.parent.mkdir(parents=True, exist_ok=True)

    # Move file and cover to destination
    os.replace(settings.output_directory / file_name, track_destination_path)
    if not (cover_destination_path).exists():
        os.replace(settings.output_directory / "cover.jpg", cover_destination_path)
    return track_destination_path, cover_destination_path
