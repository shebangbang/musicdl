from pathlib import Path

from mutagen.flac import FLAC, Picture
from mutagen.id3 import APIC, ID3, TALB, TBPM, TCOP, TDAT, TIT2, TPE1, TPE2, TPOS, TRCK, TSRC, TXXX, ID3NoHeaderError

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


def _embed_cover_flac(cover_location: Path) -> Picture:
    with cover_location.open("rb") as cover:
        picture = Picture()
        picture.type = 3
        picture.mime = "image/jpeg"
        picture.data = cover.read()
        return picture


def _embed_cover_mp3(cover_location: Path) -> APIC:
    with cover_location.open("rb") as cover:
        picture = APIC(
            encoding=3,
            mime="image/jpeg",
            type=3,
            desc="Cover",
            data=cover.read(),
        )
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

    track.add_picture(_embed_cover_flac(cover_location))
    track.save()


def write_mp3_metadata(track_location: Path, cover_location: Path, track_info: Track):
    """
    Access Track dataclass to tag the corresponding fields in the mp3 file.
    """

    try:
        tags = ID3(track_location)
        tags.clear()
    except ID3NoHeaderError:
        tags = ID3()

    for attribute, tag in MP3_TAG_MAP.items():
        value = getattr(track_info, attribute)
        if not value:
            continue

        if tag == "TIT2":
            tags.add(TIT2(encoding=3, text=str(value)))
        elif tag == "TALB":
            tags.add(TALB(encoding=3, text=str(value)))
        elif tag == "TPE1":
            tags.add(TPE1(encoding=3, text=value))
        elif tag == "TPE2":
            tags.add(TPE2(encoding=3, text=str(value)))
        elif tag == "TRCK":
            tags.add(TRCK(encoding=3, text=str(value)))
        elif tag == "TPOS":
            tags.add(TPOS(encoding=3, text=str(value)))
        elif tag == "TSRC":
            tags.add(TSRC(encoding=3, text=str(value)))
        elif tag == "TCOP":
            tags.add(TCOP(encoding=3, text=str(value)))
        elif tag == "TDAT":
            tags.add(TDAT(encoding=3, text=str(value.year)))
        elif tag == "TBPM":
            tags.add(TBPM(encoding=3, text=str(value)))
        elif "REPLAYGAIN" in tag:
            field = tag.split(":")[1]
            if "_GAIN" in field:
                formatted = _format_replay_gain("gain", value)
            else:
                formatted = _format_replay_gain("peak", value)
            tags.add(TXXX(encoding=3, desc=field, text=formatted))

    tags.add(_embed_cover_mp3(cover_location))
    tags.save(track_location)
