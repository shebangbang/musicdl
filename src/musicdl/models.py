import datetime
from dataclasses import dataclass


@dataclass
class Track:
    """
    Metadata required to download and tag a track.
    """

    title: str
    album_title: str
    artist: str
    contributing_artists: list[str]
    track_number: int
    total_tracks: int
    volume_number: int
    total_volumes: int
    isrc: str
    copyright: str
    date: datetime.date
    bpm: int | None
    replay_gain: float | None
    replay_gain_peak: float | None
    cover_tag: str | None
    download_url: str
