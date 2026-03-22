class APIError(Exception):
    def __init__(self, message):
        super().__init__(f"[API] {message}")


class InvalidIDError(APIError):
    def __init__(self):
        super().__init__("InvalidIDError: Invalid resource ID")


class MissingAPIError(APIError):
    def __init__(self):
        super().__init__(
            "MissingAPIError: Environment variable API_URL and API_URL_BAK missing"
        )


class NetworkError(APIError):
    def __init__(self):
        return super().__init__("NetworkError: Failed to communicate with the API")


class MalformedResponseError(APIError):
    def __init__(self):
        return super().__init__(
            "MalformedResponseError: Returned JSON object is malformed"
        )


class MissingDownloadURLError(APIError):
    def __init__(self):
        return super().__init__("MissingDownloadURLError: Download URL missing")


class MissingMetadataError(APIError):
    def __init__(self):
        return super().__init__("MissingMetadataError: Required metadata missing")


class ManifestParsingError(APIError):
    def __init__(self):
        return super().__init__(
            "ManifestParsingError: Download link could not be decoded and parsed from the manifest"
        )
