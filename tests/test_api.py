import base64
import json

import requests

API = "https://api.monochrome.tf"
track_id = 17342670
album_id = 204620341

# request track info
# r = requests.get(f"{API}/track/", params={"id": track_id, "quality": "LOSSLESS"})
# r = requests.get(f"{API}/album/", params={"id": album_id})
# data = r.json()
# print(data)
print()
print("lyrics")
r = requests.get(f"{API}/lyrics/", params={"id": track_id})
data = r.json()
print(data)
print()
print("track")
print()
r = requests.get(
    f"{API}/track/",
    params={"id": data["data"]["items"][0]["item"]["id"], "quality": "LOSSLESS"},
)
data = r.json()
print(data)
manifest_b64 = data["data"]["manifest"]

# decode manifest
manifest_json = base64.b64decode(manifest_b64).decode()
manifest = json.loads(manifest_json)

download_url = manifest["urls"][0]

print("Download URL:", download_url)

# download file
# audio = requests.get(download_url)

# with open("track.flac", "wb") as f:
#     f.write(audio.content)

print("Downloaded!")
