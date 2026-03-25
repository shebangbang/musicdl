from pathlib import Path

from mutagen.flac import FLAC, Picture

from musicdl.models import Track

FLAC_TAG_MAP = {
    "title": "TITLE",
    "album_title": "ALBUM",
    "artist": "ALBUMARTIST",
    "contributing_artists": "ARTIST",
    "track_number": "TRACKNUMBER",
    "total_tracks": "TRACKTOTAL",
    "volume_number": "DISCNUMBER",
    "total_volumes": "DISCTOTAL",
    "isrc": "ISRC",
    "copyright": "COPYRIGHT",
    "date": "DATE",
    "bpm": "BPM",
    "replay_gain_album_gain": "REPLAYGAIN_ALBUM_GAIN",
    "replay_gain_album_peak": "REPLAYGAIN_ALBUM_PEAK",
    "replay_gain_track_gain": "REPLAYGAIN_TRACK_GAIN",
    "replay_gain_track_peak": "REPLAYGAIN_TRACK_PEAK",
}

MP3_TAG_MAP = {
    "title": "TIT2",
    "album_title": "TALB",
    "artist": "TPE2",
    "contributing_artists": "TPE1",
    "track_number": "TRCK",
    "volume_number": "TPOS",
    "isrc": "TSRC",
    "copyright": "TCOP",
    "date": "TDAT",
    "bpm": "TBPM",
    "replay_gain_album_gain": "TXXX:REPLAYGAIN_ALBUM_GAIN",
    "replay_gain_album_peak": "TXXX:REPLAYGAIN_ALBUM_PEAK",
    "replay_gain_track_gain": "TXXX:REPLAYGAIN_TRACK_GAIN",
    "replay_gain_track_peak": "TXXX:REPLAYGAIN_TRACK_PEAK",
}


# Helper functions
def _format_replay_gain(type: str, value: float) -> str:
    if type == "gain":
        return f"{value:.2f} dB"
    else:
        return f"{value:.6f}"


def _embed_cover(cover_location: Path) -> Picture:
    with cover_location.open("rb") as cover:
        picture = Picture()
        picture.type = 3
        picture.mime = "image/jpeg"
        picture.data = cover.read()
        return picture


def write_flac_metadata(track_location: Path, cover_location: Path, track_info: Track):
    """
    Access Track dataclass to tag the corresponding fields in the flac file.
    """
    track = FLAC(track_location)
    track.clear()
    track.clear_pictures()

    for attribute, tag in FLAC_TAG_MAP.items():
        value = getattr(track_info, attribute)
        if not value:
            continue

        if tag == "ARTIST":
            track[tag] = value
        elif tag == "DATE":
            track[tag] = str(value.year)
        elif "_GAIN" in tag:
            track[tag] = _format_replay_gain("gain", value)
        elif "_PEAK" in tag:
            track[tag] = _format_replay_gain("peak", value)
        else:
            track[tag] = str(value)

    track.add_picture(_embed_cover(cover_location))
    track.save()


def write_mp3_metadata(track_location: Path, cover_location: Path, track_info: Track):
    """
    Access Track dataclass to tag the corresponding fields in the flac file.
    """

    # TODO: Implement mp3 tagging
    pass
