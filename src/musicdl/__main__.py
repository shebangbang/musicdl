"""
Entry-point module, in case you use `uv run python -m musicdl`.

Why does this file exist, and why `__main__`? For more info, read:
- https://www.python.org/dev/peps/pep-0338/
- https://docs.python.org/3/using/cmdline.html#cmdoption-m
"""

from __future__ import annotations

import sys

from .main import main

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

# import argparse
# import base64
# import json
#
# import requests
#
# API = "https://api.monochrome.tf"
# track_id = 68737746
# playlist_id = "4c0ff54f-8029-45a5-affa-129500d62a5d"
#
# # request track info
# # r = requests.get(f"{API}/track/", params={"id": track_id, "quality": "LOSSLESS"})
# r = requests.get(f"{API}/playlist/", params={"id": playlist_id})
# data = r.json()
# r = requests.get(
#     f"{API}/track/",
#     params={"id": data["items"][0]["item"]["id"], "quality": "LOSSLESS"},
# )
# data = r.json()
# print(data)
# manifest_b64 = data["data"]["manifest"]
#
# # decode manifest
# manifest_json = base64.b64decode(manifest_b64).decode()
# manifest = json.loads(manifest_json)
#
# download_url = manifest["urls"][0]
#
# print("Download URL:", download_url)
#
# # download file
# audio = requests.get(download_url)
#
# with open("track.flac", "wb") as f:
#     f.write(audio.content)
#
# print("Downloaded!")
