# musicdl

A command line tool to simplify the process of downloading tracks through Tidal's API.

NOTE: You must have a premium Tidal subscription in order to use the API. Additionally, in order to download through aria2, please [install](https://github.com/aria2/aria2) it separately.

## Features

- Simple CLI
- Add individual tracks, or an album
- Download files using `aria2c`

## Installation

```bash
git clone https://github.com/arlechinus/musicdl
cd musicdl
uv sync
uv run musicdl
```

## Options and Flags

    -h,     --help                      Print this help message and exit
    -t,     --token     TEXT            Set API token and save it locally
    -o,     --output    TEXT            Specify path for output files

## API Token

- Linux/macOS:

```bash
export TIDAL_API_TOKEN=your_token_here
```

- Windows (PowerShell):

```powershell
$env:TIDAL_API_TOKEN=your_token_here
```
