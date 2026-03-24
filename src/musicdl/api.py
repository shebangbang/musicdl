import base64
import binascii
import datetime
import json
import os
from enum import Enum
from typing import Any

import requests

from musicdl.exceptions import (
    APINetworkError,
    InvalidIDError,
    MalformedResponseError,
    ManifestParsingError,
    MissingAPIError,
    MissingDownloadURLError,
    MissingMetadataError,
)
from musicdl.models import Track

try:
    TIMEOUT = int(os.environ["TIMEOUT"])
except KeyError:
    TIMEOUT = 3


class Resource(Enum):
    INFO = "info"
    TRACK = "track"
    ALBUM = "album"
    ARTIST = "artist"
    PLAYLIST = "playlist"
    COVER = "cover"


# helper functions
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
    valid_fields = {"data", "playlist", "items", "artist", "albums", "tracks"}
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
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Connection": "keep-alive",
            }
        )

    def _fetch_resource_info(
        self, resource_type: Resource, resource_id: int
    ) -> dict[str, Any]:
        """
        Generic resource info fetcher.
        """
        parameters = {"id": resource_id}
        if resource_type == Resource.TRACK:
            try:
                parameters["quality"] = os.environ["QUALITY"]
            except KeyError:
                parameters["quality"] = "LOSSLESS"
        try:
            r = self.session.get(
                f"{self.api}/{resource_type.value}/",
                params=parameters,
                timeout=TIMEOUT,
            )
            r.raise_for_status()
        except requests.exceptions.ConnectionError:
            raise APINetworkError
        except requests.exceptions.HTTPError:
            raise InvalidIDError

        data = r.json()
        if _check_response_validity(data):
            return data
        else:
            raise MalformedResponseError

    def fetch_track_info(self, track_id: int) -> Track:
        # fetch info
        track_data = self._fetch_resource_info(Resource.INFO, track_id)["data"]

        album_id = track_data["album"]["id"]
        album_metadata = self._fetch_resource_info(Resource.ALBUM, album_id)["data"]

        track_location = self._fetch_resource_info(Resource.TRACK, track_id)["data"]
        download_url = _decode_and_parse_manifest(track_location["manifest"])

        # create track object
        try:
            track = Track(
                track_data["title"],
                track_data["album"]["title"],
                track_data["artist"]["name"],
                [artist["name"] for artist in track_data["artists"]],
                track_data["trackNumber"],
                album_metadata["numberOfTracks"],
                track_data["volumeNumber"],
                album_metadata["numberOfVolumes"],
                track_data["isrc"],
                track_data["copyright"],
                datetime.datetime.strptime(
                    album_metadata["releaseDate"], "%Y-%m-%d"
                ).date(),
                track_data["bpm"],
                track_data["replayGain"],
                track_data["peak"],
                track_data["album"]["cover"],
                download_url,
            )
        except KeyError:
            raise MissingMetadataError

        return track

    @classmethod
    def from_env(cls):
        """
        Helper to create an object with a value from the environment.
        """
        try:
            api = os.environ["API_URL"]
        except KeyError:
            try:
                api = os.environ["API_URL_BAK"]
            except KeyError:
                raise MissingAPIError
        return cls(api)
