# StreamSniper v2.0

Video and audio downloader with a dark-themed Tkinter GUI, powered by yt-dlp.

Supports YouTube and [1800+ other sites](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md).

## Features

- Video download (MP4) with quality selection (best, 1080p, 720p, 480p)
- Audio extraction (MP3, M4A, OPUS, WAV, FLAC) with embedded thumbnails
- Thumbnail preview and video info display before downloading
- Live progress bar with speed, ETA, and file size
- Searchable download history
- Persistent settings (download directory, default format, quality)
- Dark UI with navy-to-burgundy gradient

## Requirements

- Python 3.10+ with tkinter
- ffmpeg (for audio extraction and format merging)
- yt-dlp

### macOS (Homebrew)

```bash
brew install python-tk@3.12 ffmpeg yt-dlp
```

### pip

```bash
pip install yt-dlp Pillow
```

## Usage

```bash
python3.12 run.py
```

## License

GPLv3
