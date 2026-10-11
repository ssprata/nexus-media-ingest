# Nexus — High-Speed Media Ingest

Nexus is a high-speed, multi-threaded desktop media batch ingest and download manager designed for Windows. It features customizable hierarchical download profiles, support for multiple download engines, and a sleek neon user interface. 

The application serves as a high-performance graphical front-end for popular command-line utilities, including `aria2c` for high-speed file transfers, `yt-dlp` for video and audio extraction, and `gallery-dl` for image board gallery scraping. By wrapping these command-line tools in a PyQt6 graphical interface, it simplifies direct downloading, batch scheduling, profile management, and post-processing.

---

## Key Features

* **Hierarchical Profile Management**: Organize download profiles into expandable and collapsible category folders. This is configured locally via a structured JSON configuration.
* **Main Ingest Root & Auto-Mirrored Folders**: Set a central library root folder. The app automatically creates matching folders and sub-folders on disk (`<Library Root>/<Folder>/<Profile Name>`), ensuring total cross-PC portability without breaking drive paths (`F:`, `G:`, `C:`).
* **Portable Profile Packages (.nexus / .json)**: One-click export and import of all profiles, individual category folders, or single presets with merge and overwrite support.
* **Tree Context Menu**: Right-click any category folder or profile to open directly in Windows Explorer, export packages, add sub-profiles, or delete items.
* **Smart Concurrency Queue**: Regulate simultaneous downloads (1 to 6 concurrent workers) to prevent network congestion or CPU lockup. Queued downloads start automatically as active transfers complete.
* **Multi-Engine Media Support**:
  * **aria2c**: Extreme multi-connection chunked downloads with resume flags (`-c`, `--auto-file-renaming=false`).
  * **yt-dlp**: High-speed video/audio extraction with subtitle embedding, custom transcode formats, and precise file tracking.
  * **spotdl**: Seamless Spotify track, album, and playlist downloader with automated FFmpeg audio encoding and cookie support.
  * **gallery-dl** & **instaloader**: Image board and Instagram profile media scrapers.
* **Persistent Ingest History**: Dedicated history hub tracking file names, URLs, file sizes, timestamps, and profiles, complete with real-time text filtering, direct folder opening, and URL clipboard copying.
* **Drag-and-Drop Reorganization**: Move profile cards between category folders directly through the graphical user interface. Changes are immediately persisted in the configuration file.
* **Real-time Download Metrics**: Background threads parse stdout streams to display live progress metrics (percentage, speed, ETA) along with an aggregate speed monitor across all active jobs.
* **System Tray & Close Guard**: Minimize to tray with background operation, plus intelligent quit confirmation if active downloads are still transferring.
* **Automated Bootstrap**: Checks for missing required engine binaries on launch and auto-downloads them dynamically using an integrated splash loader.

---

## Directory Structure

```
nexus-media-ingest/
├── .gitignore
├── config.json              # Active settings, categories, and profiles store
├── history.json             # Persistent download history records
├── pyproject.toml           # Project metadata and packaging configuration
├── package.json             # Application definition and script runner metadata
├── requirements.txt         # Python dependencies (PyQt6, requests, spotdl, instaloader)
├── run.bat                  # Bootstrap and launcher script
├── main.py                  # Entry bootstrap script (validates requirements and launches GUI)
├── config_manager.py        # Logic for loading, saving, and updating profile configurations
├── history_manager.py       # Thread-safe persistent ingest history store
├── dependency_manager.py    # Binary manager for downloading and extracting required executables
├── downloader.py            # Asynchronous subprocess management, queue workers, and stdout regex parsing
├── bin/                     # Auto-generated directory containing local CLI binaries
│   ├── aria2c.exe           # High-speed download engine
│   ├── yt-dlp.exe           # Media downloader engine
│   ├── gallery-dl.exe       # Optional gallery scraper engine
│   ├── ffmpeg.exe           # Optional post-processing converter
│   └── ffprobe.exe          # Optional media streams analyzer
└── ui/
    ├── styles.py            # Nexus neon stylesheet definitions (QSS)
    └── main_window.py       # Main GUI layout, Queue, History, Settings, custom dialogs, and tray icon
```

---

## Quick Start Guide

### Prerequisites

Nexus is designed to run on Windows 10 or Windows 11. It requires Python 3.8 or newer.

If Python is not installed on your system or is missing from your system `PATH`, the bootstrap launcher will automatically download and install Python 3.11.9 to your user profile directory (`%LOCALAPPDATA%\Programs\Python\Python311`).

### Running the Application

1. Clone or download this repository.
2. Double-click the **`run.bat`** file in the root directory.
3. The bootstrap script will:
   * Detect or install Python.
   * Create a local virtual environment in the `.venv` directory.
   * Upgrade `pip` and install all dependencies listed in `requirements.txt`.
   * Start the PyQt6 application.
4. On the first launch, the boot splash screen will automatically fetch the core binaries (`aria2c.exe` and `yt-dlp.exe`) and place them in the `bin/` subdirectory.

---

## Configuration Schema

All settings, profiles, and directories are stored in `config.json`. The application auto-generates this file on launch if it is missing.

### Configuration Format Example

```json
{
  "active_profile": "Downloads",
  "profiles": [
    {
      "name": "Web Media MP4",
      "tool": "yt-dlp",
      "folder": "Videos",
      "export_dir": "",
      "aria2_settings": {
        "max_connection_per_server": 16,
        "split": 16,
        "max_download_limit": "0",
        "custom_flags": ""
      },
      "ytdlp_settings": {
        "format": "bestvideo+bestaudio/best",
        "video_format": "mp4",
        "extract_audio": false,
        "audio_format": "mp3",
        "audio_quality": "0",
        "embed_subs": false,
        "custom_flags": ""
      },
      "gallerydl_settings": {
        "custom_flags": ""
      }
    },
    {
      "name": "Nexus Ingest",
      "tool": "aria2c",
      "folder": "Nexus Ingest",
      "export_dir": "C:\\Users\\User\\Downloads\\Nexus Ingest",
      "aria2_settings": {
        "max_connection_per_server": 16,
        "split": 16,
        "max_download_limit": "0",
        "custom_flags": ""
      },
      "ytdlp_settings": {
        "format": "bestaudio/best",
        "video_format": "best",
        "extract_audio": false,
        "audio_format": "mp3",
        "audio_quality": "5",
        "embed_subs": false,
        "custom_flags": ""
      },
      "gallerydl_settings": {
        "custom_flags": ""
      }
    }
  ]
}
```

### Profile Field Description

| Field | Type | Description |
| :--- | :--- | :--- |
| `name` | String | Unique identifier for the download profile. |
| `tool` | String | The selected engine for the profile: `"aria2c"`, `"yt-dlp"`, or `"gallery-dl"`. |
| `folder` | String | The parent category folder name. |
| `export_dir` | String | Directory where downloaded files will be saved. |
| `aria2_settings` | Object | Connection, split, and bandwidth settings specific to aria2c execution. |
| `ytdlp_settings` | Object | Target format, video container format, audio extraction options, and quality settings for yt-dlp. |
| `gallerydl_settings` | Object | Custom command-line flags and parameters for gallery-dl extraction. |

---

## Subprocess Execution and Regex Metrics Extraction

Downloads are spawned asynchronously using Python's `subprocess.Popen`. Standard output and standard error streams are redirected, read on separate background threads, and matched against regex patterns to calculate metrics:

* **aria2c Parsing**: Matches percent progress `(15%)`, current speed `CN:16 DL:4.2MiB`, and connection counts.
* **yt-dlp Parsing**: Matches progress patterns `[download]  45.2% of  120.50MiB at  3.12MiB/s ETA 00:24`.
* **gallery-dl Parsing**: Logs output matching downloaded targets.

---

## Author & Credits

Created and maintained by **[@ssprata](https://github.com/ssprata)**  
* GitHub: [https://github.com/ssprata](https://github.com/ssprata)
* Project Repository: [https://github.com/ssprata/multi-downloader-tool](https://github.com/ssprata/multi-downloader-tool)

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details. Built using open-source utilities (`yt-dlp`, `aria2`, `ffmpeg`, `spotdl`, `gallery-dl`, `instaloader`).
