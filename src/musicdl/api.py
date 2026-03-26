import base64
import binascii
import datetime
import json
import logging
from enum import Enum
from typing import Any

import requests

from musicdl.config import settings
from musicdl.exceptions import (
    APINetworkError,
    APIRequestTimeout,
    InvalidIDError,
    MalformedJSONError,
    ManifestParsingError,
    MissingDownloadURLError,
    MissingMetadataError,
)
from musicdl.models import Track

logger = logging.getLogger(__name__)


class Resource(Enum):
    INFO = "info"
    TRACK = "track"
    ALBUM = "album"
    ARTIST = "artist"
    PLAYLIST = "playlist"
    COVER = "cover"


# Helper functions
def _decode_and_parse_manifest(manifest: str) -> str:
    try:
        manifest_json = base64.b64decode(manifest).decode()
        final_manifest = json.loads(manifest_json)
        download_url = final_manifest["urls"][0]
    except IndexError:
        raise MissingDownloadURLError
    except TypeError, binascii.Error, json.JSONDecodeError:
        raise ManifestParsingError

    return download_url


def _check_response_validity(data: dict[str, Any]) -> bool:
    valid_fields = {"data", "playlist", "items", "artist", "albums", "tracks", "covers"}
    if "version" in data and len(data) >= 2:
        if any(field in data for field in valid_fields):
            return True
    return False


class APIClient:
    """
    High-level client for the remote music API.
    """

    def __init__(self, api: str):
        self.api = api
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Connection": "keep-alive",
        })

    def _fetch_resource_info(self, resource_type: Resource, resource_id: str) -> dict[str, Any]:
        """
        Generic resource info fetcher.
        """
        parameters = {"id": resource_id}
        if resource_type == Resource.TRACK:
            parameters["quality"] = settings.quality
        try:
            r = self.session.get(
                f"{self.api}/{resource_type.value}/",
                params=parameters,
                timeout=settings.timeout,
            )
            r.raise_for_status()
        except requests.exceptions.ConnectionError:
            raise APINetworkError
        except requests.exceptions.HTTPError:
            raise InvalidIDError
        except requests.exceptions.ReadTimeout:
            raise APIRequestTimeout

        data = r.json()
        if _check_response_validity(data):
            return data
        else:
            raise MalformedJSONError

    def fetch_track_info(self, track_id: str, album_metadata: dict | None = None) -> Track:
        # Fetch info
        track_data = self._fetch_resource_info(Resource.INFO, track_id)["data"]

        if not album_metadata:
            album_id = track_data["album"]["id"]
            album_metadata = self._fetch_resource_info(Resource.ALBUM, album_id)["data"]

        cover_url = self._fetch_resource_info(Resource.COVER, track_id)["covers"][0]
        cover_url = cover_url.get("1280") or cover_url.get("640")

        track_location = self._fetch_resource_info(Resource.TRACK, track_id)["data"]
        download_url = _decode_and_parse_manifest(track_location["manifest"])
        if track_location["audioQuality"] != settings.quality:
            logger.debug("Dropping quality due to unavailability")
            settings.quality = track_location["audioQuality"]

        title_combined = (
            f"{track_data['title']} ({track_data['version']})" if track_data["version"] else track_data["title"]
        )
        # Create track object
        try:
            track = Track(
                title_combined,
                track_data["album"]["title"],
                track_data["artist"]["name"],
                [artist["name"] for artist in track_data["artists"]],
                track_data["trackNumber"],
                album_metadata["numberOfTracks"],
                track_data["volumeNumber"],
                album_metadata["numberOfVolumes"],
                track_data["isrc"],
                track_data["copyright"],
                datetime.datetime.strptime(album_metadata["releaseDate"], "%Y-%m-%d").date(),
                track_data["bpm"],
                track_location["albumReplayGain"],
                track_location["albumPeakAmplitude"],
                track_data["replayGain"],
                track_data["peak"],
                cover_url,
                download_url,
            )
        except KeyError:
            raise MissingMetadataError

        return track

    def fetch_album_info(self, album_id: str) -> list[Track]:
        tracks = []
        album_metadata = self._fetch_resource_info(Resource.ALBUM, album_id)["data"]
        for track_info in album_metadata["items"]:
            tracks.append(self.fetch_track_info(track_info["item"]["id"], album_metadata))

        return tracks

    def fetch_playlist_info(self, playlist_uuid: str) -> list[Track]:
        tracks = []
        playlist_metadata = self._fetch_resource_info(Resource.PLAYLIST, playlist_uuid)
        for track_info in playlist_metadata["items"]:
            tracks.append(self.fetch_track_info(track_info["item"]["id"]))

        return tracks
