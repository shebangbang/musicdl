# musicdl

A command line tool to simplify the process of downloading tracks through Tidal's API.

NOTE: You must have a premium Tidal subscription in order to use the API.

## Features

- Simple CLI
- Add individual tracks, or an album
- Download files

## Installation

```bash
git clone https://github.com/arlechinus/musicdl
cd musicdl
uv sync
uv run musicdl
```

## Options and Flags

```bash
positional arguments:
    {track,album}       Resource Type
    resource_id         Resource ID

options:
    -h, --help          show this help message and exit
    -l, --license       Show license information and exit
    -f, --folder FOLDER Output folder path
    -q, --quiet         Use quiet output
    -v, --verbose       Use verbose output
```

## API Token

- Linux/macOS:

```bash
export TIDAL_API_TOKEN=your_token_here
```
