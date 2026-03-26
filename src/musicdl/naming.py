from pathlib import Path

from musicdl.config import settings
from musicdl.models import Track


def _sanitize_file_name(file_name: str) -> str:
    illegal_chars = ':/?*"<>|\\'
    for char in illegal_chars:
        if char in file_name:
            file_name.replace(char, "-")
    return file_name


def _generate_folder_names(track: Track) -> tuple[str, str]:
    parent_folder = _sanitize_file_name(track.artist)
    child_folder = f"({track.date.year}) {_sanitize_file_name(track.album_title)}"
    return parent_folder, child_folder


def generate_file_name(track: Track) -> tuple[str, str]:
    file_extension = "mp3" if settings.quality in ("HIGH", "LOW") else "flac"
    file_name = f"{track.track_number:02d}. {_sanitize_file_name(track.title)}.{file_extension}"
    return file_name, file_extension


def generate_destination_path(track: Track) -> tuple[Path, Path]:
    # Generate file names
    parent_path, child_path = _generate_folder_names(track)
    track_destination_path = settings.output_directory / parent_path / child_path
    cover_destination_path = track_destination_path

    # Multiple volumes check
    if track.total_volumes > 1:
        track_destination_path = track_destination_path / f"Disc {track.volume_number:02d}"

    return track_destination_path, cover_destination_path
