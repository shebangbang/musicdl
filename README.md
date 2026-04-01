# musicdl

A command line tool to simplify the process of downloading tracks through the HiFi-API.

> [!IMPORTANT]
> Music piracy is illegal in most countries. This project is intended for use with a valid Tidal account for educational purposes only for example, in your homelab.

## Features

- Simple CLI
- Download individual tracks, albums, or playlists
- Search for tracks or albums using a query

## Installation

```bash
git clone https://github.com/arlechinus/musicdl
cd musicdl
uv sync
uv run musicdl --help
```

## Options and Flags

```bash
positional arguments:
    {download,search}       Action
    {track,album,playlist}  Resource Type
    resource_id             Resource ID

options:
    -h, --help              show this help message and exit
    -l, --license           Show license information and exit
    -f, --folder FOLDER     Output folder path
    -q, --quiet             Use quiet output
    -v, --verbose           Use verbose output
```
