import os

from musicdl.config import settings
from musicdl.models import Track


def generate_filename(track: Track) -> str:
    file_extension = ".mp3" if settings.quality in ("HIGH", "LOW") else ".flac"
    file_name = f"{track.track_number: 03d}. {track.title}{file_extension}"
    return file_name
