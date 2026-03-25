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
    replay_gain_album_gain: float | None
    replay_gain_album_peak: float | None
    replay_gain_track_gain: float | None
    replay_gain_track_peak: float | None
    cover_url: str
    download_url: str
