import os
import stat
import time
import zipfile
import requests
import tempfile
import shutil

BIN_DIR = os.path.abspath("bin")
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

TOOLS = {
    "yt-dlp": {
        "filename": "yt-dlp.exe",
        "url": "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe",
        "is_zip": False
    },
    "aria2c": {
        "filename": "aria2c.exe",
        "url": "https://github.com/aria2/aria2/releases/download/release-1.37.0/aria2-1.37.0-win-64bit-build1.zip",
        "is_zip": True,
        "extract_target": "aria2c.exe"
    },
    "gallery-dl": {
        "filename": "gallery-dl.exe",
        "url": "https://github.com/mikf/gallery-dl/releases/download/v1.30.8/gallery-dl.exe",
        "is_zip": False
    },
    "ffmpeg": {
        "filename": "ffmpeg.exe",
        "url": "https://github.com/GyanD/codexffmpeg/releases/download/7.0.1/ffmpeg-7.0.1-essentials_build.zip",
        "is_zip": True,
        "extract_target": ["ffmpeg.exe", "ffprobe.exe"]
    },
    "spotdl": {
        "filename": "spotdl.exe",
        "url": "https://github.com/spotDL/spotify-downloader/releases/download/v4.5.2/spotdl-4.5.2-win32.exe",
        "is_zip": False
    },
    "instagram": {
        "filename": "instaloader",
        "url": "",
        "is_zip": False
    }
}


def _safe_remove(file_path):
    """Safely removes a file if it exists, resetting permissions if necessary."""
    if not os.path.exists(file_path):
        return
    try:
        os.chmod(file_path, stat.S_IWRITE)
        os.remove(file_path)
    except Exception:
        pass


def _safe_replace_file(src_path, dst_path, retries=4, delay=0.3):
    """
    Safely replaces dst_path with src_path on Windows, handling locks,
    read-only attributes, and fallback renaming if in-use.
    """
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)

    if os.path.exists(dst_path):
        try:
            os.chmod(dst_path, stat.S_IWRITE)
        except Exception:
            pass

    for attempt in range(retries):
        try:
            if os.path.exists(dst_path):
                os.replace(src_path, dst_path)
            else:
                shutil.move(src_path, dst_path)
            return True
        except (PermissionError, OSError) as e:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                # Windows fallback: rename locked destination to .old and move new file
                try:
                    old_path = f"{dst_path}.old_{int(time.time())}"
                    _safe_remove(old_path)
                    os.rename(dst_path, old_path)
                    shutil.move(src_path, dst_path)
                    _safe_remove(old_path)
                    return True
                except Exception as ex:
                    raise PermissionError(f"Could not replace '{dst_path}': {e} -> {ex}")
    return False


def _cleanup_old_binaries():
    """Cleans up leftover .old and .tmp binary files in BIN_DIR."""
    if not os.path.exists(BIN_DIR):
        return
    for item in os.listdir(BIN_DIR):
        if item.endswith(".old") or ".old_" in item or item.endswith(".tmp"):
            _safe_remove(os.path.join(BIN_DIR, item))


class DependencyManager:
    def __init__(self):
        os.makedirs(BIN_DIR, exist_ok=True)
        _cleanup_old_binaries()

    def get_tool_path(self, name):
        """Get the absolute path of a tool. Returns None if not found/installed."""
        if name not in TOOLS:
            return None
        
        if name == "instagram":
            try:
                import instaloader
                import sys
                return sys.executable
            except ImportError:
                return None

        info = TOOLS[name]
        if name == "ffmpeg":
            ffmpeg_path = os.path.join(BIN_DIR, "ffmpeg.exe")
            ffprobe_path = os.path.join(BIN_DIR, "ffprobe.exe")
            if os.path.exists(ffmpeg_path) and os.path.exists(ffprobe_path):
                return ffmpeg_path
        else:
            path = os.path.join(BIN_DIR, info["filename"])
            if os.path.exists(path):
                return path
        return None

    def is_installed(self, name):
        return self.get_tool_path(name) is not None

    def check_core_dependencies(self):
        """Returns True if core dependencies (yt-dlp, aria2c, and ffmpeg) are installed."""
        return self.is_installed("yt-dlp") and self.is_installed("aria2c") and self.is_installed("ffmpeg")

    def get_tool_version(self, name):
        """Returns the version string of the tool if installed, else None."""
        path = self.get_tool_path(name)
        if not path:
            return None
        
        import subprocess
        creationflags = 0
        if os.name == 'nt':
            creationflags = subprocess.CREATE_NO_WINDOW

        try:
            if name == "yt-dlp":
                res = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=5, creationflags=creationflags)
                if res.returncode == 0 and res.stdout.strip():
                    return res.stdout.strip()
            elif name == "aria2c":
                res = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=5, creationflags=creationflags)
                if res.returncode == 0:
                    first_line = res.stdout.splitlines()[0] if res.stdout.splitlines() else ""
                    return first_line.replace("aria2 version ", "").strip()
            elif name == "ffmpeg":
                res = subprocess.run([path, "-version"], capture_output=True, text=True, timeout=5, creationflags=creationflags)
                if res.returncode == 0:
                    first_line = res.stdout.splitlines()[0] if res.stdout.splitlines() else ""
                    parts = first_line.split("version")
                    return parts[1].split(" ")[1].strip() if len(parts) > 1 else "Installed"
            elif name == "gallery-dl":
                res = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=5, creationflags=creationflags)
                if res.returncode == 0 and res.stdout.strip():
                    return res.stdout.strip()
            elif name == "spotdl":
                res = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=5, creationflags=creationflags)
                if res.returncode == 0 and res.stdout.strip():
                    return res.stdout.strip()
            elif name == "instagram":
                import instaloader
                return getattr(instaloader, "__version__", "Installed")
        except Exception:
            return "Installed"
        return "Installed"

    def update_tool(self, name, progress_callback=None):
        """Updates a tool to the latest version."""
        _cleanup_old_binaries()
        if name == "yt-dlp":
            path = self.get_tool_path("yt-dlp")
            if path and os.path.exists(path):
                import subprocess
                creationflags = 0
                if os.name == 'nt':
                    creationflags = subprocess.CREATE_NO_WINDOW
                if progress_callback:
                    progress_callback(30.0)
                try:
                    res = subprocess.run([path, "-U"], capture_output=True, text=True, timeout=30, creationflags=creationflags)
                    if res.returncode == 0:
                        _cleanup_old_binaries()
                        if progress_callback:
                            progress_callback(100.0)
                        return path
                except Exception:
                    pass
        # Direct download / install
        return self.download_tool(name, progress_callback=progress_callback)

    def download_tool(self, name, progress_callback=None):
        """
        Downloads a tool. progress_callback is called with (percent: float)
        """
        if name not in TOOLS:
            raise ValueError(f"Unknown tool: {name}")

        _cleanup_old_binaries()

        if name == "instagram":
            import subprocess
            import sys
            try:
                if progress_callback:
                    progress_callback(20.0)
                
                creationflags = 0
                if os.name == 'nt':
                    creationflags = subprocess.CREATE_NO_WINDOW
                
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "--upgrade", "instaloader"],
                    check=True,
                    capture_output=True,
                    timeout=90,
                    creationflags=creationflags
                )
                
                if progress_callback:
                    progress_callback(100.0)
                return sys.executable
            except Exception as e:
                raise Exception(f"Failed to install/upgrade instaloader package: {e}")

        info = TOOLS[name]
        url = info["url"]
        
        # Dynamically query latest spotdl release version
        if name == "spotdl":
            try:
                response_api = requests.get(
                    "https://api.github.com/repos/spotDL/spotify-downloader/releases/latest",
                    headers=DEFAULT_HEADERS,
                    timeout=8
                )
                if response_api.status_code == 200:
                    data = response_api.json()
                    for asset in data.get("assets", []):
                        asset_name = asset.get("name", "")
                        if asset_name.endswith(".exe") and "win" in asset_name.lower():
                            url = asset.get("browser_download_url")
                            break
            except Exception as e:
                print(f"Failed to fetch dynamic spotdl url, using fallback: {e}")

        # Dynamically query latest gallery-dl release with windows binary
        if name == "gallery-dl":
            try:
                response_api = requests.get(
                    "https://api.github.com/repos/mikf/gallery-dl/releases",
                    headers=DEFAULT_HEADERS,
                    timeout=8
                )
                if response_api.status_code == 200:
                    for rel in response_api.json():
                        for asset in rel.get("assets", []):
                            if asset.get("name") == "gallery-dl.exe":
                                url = asset.get("browser_download_url")
                                break
                        if url != info["url"]:
                            break
            except Exception as e:
                print(f"Failed to fetch dynamic gallery-dl url, using fallback: {e}")
        
        # Download file to a temp location
        response = requests.get(url, headers=DEFAULT_HEADERS, stream=True, timeout=20)
        if response.status_code != 200:
            raise Exception(f"Failed to download tool from {url} (status code: {response.status_code})")

        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        suffix = ".zip" if info["is_zip"] else ".exe"

        fd, temp_path = tempfile.mkstemp(suffix=suffix)
        try:
            with os.fdopen(fd, 'wb') as temp_file:
                for chunk in response.iter_content(chunk_size=1024 * 64):
                    if chunk:
                        temp_file.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total_size > 0:
                            percent = (downloaded / total_size) * 100
                            progress_callback(percent)

            # Process extraction or moving
            if info["is_zip"]:
                with zipfile.ZipFile(temp_path, 'r') as zip_ref:
                    targets = info["extract_target"]
                    if isinstance(targets, str):
                        targets = [targets]
                    
                    extracted_count = 0
                    for file_info in zip_ref.infolist():
                        basename = os.path.basename(file_info.filename)
                        if basename in targets:
                            target_dest = os.path.join(BIN_DIR, basename)
                            temp_extract_fd, temp_extract_path = tempfile.mkstemp(suffix=f"_{basename}")
                            try:
                                with zip_ref.open(file_info) as source, os.fdopen(temp_extract_fd, 'wb') as dest:
                                    shutil.copyfileobj(source, dest)
                                _safe_replace_file(temp_extract_path, target_dest)
                                extracted_count += 1
                            finally:
                                _safe_remove(temp_extract_path)
                    
                    if extracted_count == 0:
                        raise Exception(f"Targets {targets} not found in zip archive.")
            else:
                dest_path = os.path.join(BIN_DIR, info["filename"])
                _safe_replace_file(temp_path, dest_path)
                
        finally:
            _safe_remove(temp_path)
            _cleanup_old_binaries()
        
        if progress_callback:
            progress_callback(100.0)

        return self.get_tool_path(name)
