import os
import re
import json
import subprocess
import shlex
from PyQt6.QtCore import QThread, pyqtSignal

_cached_h264_encoder = None

def get_best_h264_encoder_args(ffmpeg_exe):
    """Detects and returns optimal GPU or fast CPU H.264 encoder parameters."""
    global _cached_h264_encoder
    if _cached_h264_encoder is not None:
        return _cached_h264_encoder

    creationflags = 0
    if os.name == 'nt':
        creationflags = subprocess.CREATE_NO_WINDOW

    # 1. Test AMD AMF (Fast GPU on AMD Radeon)
    try:
        r = subprocess.run(
            [ffmpeg_exe, "-f", "lavfi", "-i", "color=c=black:s=1920x1080:d=0.04", "-c:v", "h264_amf", "-f", "null", "-"],
            capture_output=True, text=True, creationflags=creationflags, timeout=5
        )
        if r.returncode == 0:
            _cached_h264_encoder = ["-c:v", "h264_amf", "-rc", "cqp", "-qp_i", "18", "-qp_p", "20", "-quality", "speed"]
            return _cached_h264_encoder
    except Exception:
        pass

    # 2. Test NVIDIA NVENC (Fast GPU on GeForce)
    try:
        r = subprocess.run(
            [ffmpeg_exe, "-f", "lavfi", "-i", "color=c=black:s=1920x1080:d=0.04", "-c:v", "h264_nvenc", "-f", "null", "-"],
            capture_output=True, text=True, creationflags=creationflags, timeout=5
        )
        if r.returncode == 0:
            _cached_h264_encoder = ["-c:v", "h264_nvenc", "-preset", "p4", "-cq", "19"]
            return _cached_h264_encoder
    except Exception:
        pass

    # 3. Test Intel QSV
    try:
        r = subprocess.run(
            [ffmpeg_exe, "-f", "lavfi", "-i", "color=c=black:s=1920x1080:d=0.04", "-c:v", "h264_qsv", "-f", "null", "-"],
            capture_output=True, text=True, creationflags=creationflags, timeout=5
        )
        if r.returncode == 0:
            _cached_h264_encoder = ["-c:v", "h264_qsv", "-global_quality", "20"]
            return _cached_h264_encoder
    except Exception:
        pass

    # 4. Multithreaded CPU libx264 fallback
    _cached_h264_encoder = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18"]
    return _cached_h264_encoder


def probe_media_codecs(file_path, ffprobe_exe):
    """Returns (vcodec, acodec, duration_sec) using ffprobe."""
    try:
        cmd = [
            ffprobe_exe, "-v", "error",
            "-show_entries", "format=duration:stream=index,codec_type,codec_name",
            "-of", "json", file_path
        ]
        creationflags = 0
        if os.name == 'nt':
            creationflags = subprocess.CREATE_NO_WINDOW
        res = subprocess.run(cmd, capture_output=True, text=True, creationflags=creationflags, timeout=10)
        if res.returncode == 0 and res.stdout:
            data = json.loads(res.stdout)
            vcodec, acodec = None, None
            duration = float(data.get("format", {}).get("duration", 0.0) or 0.0)
            for s in data.get("streams", []):
                ctype = s.get("codec_type")
                cname = (s.get("codec_name") or "").lower()
                if ctype == "video" and not vcodec:
                    vcodec = cname
                elif ctype == "audio" and not acodec:
                    acodec = cname
            return vcodec, acodec, duration
    except Exception:
        pass
    return None, None, 0.0

def extract_browser_cookies(browser_name, output_path="cookies.txt"):
    """Extracts cookies from an installed browser using yt-dlp cookie jar and saves to Netscape cookies.txt."""
    import yt_dlp.cookies
    b_name = browser_name.lower().strip()
    try:
        cookie_jar = yt_dlp.cookies.extract_cookies_from_browser(b_name)
        if cookie_jar and len(cookie_jar) > 0:
            cookie_jar.save(output_path, format="netscape")
            return True, f"Successfully extracted {len(cookie_jar)} cookies from {browser_name.capitalize()}!"
        else:
            return False, f"No cookies found in {browser_name.capitalize()} profile."
    except Exception as e:
        err_msg = str(e)
        if "Could not copy Chrome cookie database" in err_msg or "Permission denied" in err_msg:
            return False, f"{browser_name.capitalize()} is currently open and locking its cookie file.\n\nPlease close {browser_name.capitalize()} and try again, or paste cookies directly."
        elif "Failed to decrypt" in err_msg:
            return False, f"{browser_name.capitalize()} encryption error: {err_msg}\n\nTry using Firefox or pasting cookies via clipboard."
        return False, f"Extraction failed: {err_msg}"

def get_cookie_status(cookie_path="cookies.txt"):
    """Checks if cookies.txt exists and returns cookie count and status."""
    if not os.path.exists(cookie_path):
        return False, 0, "No cookies loaded (Anonymous Mode)"
    try:
        count = 0
        has_youtube = False
        with open(cookie_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line_s = line.strip()
                if line_s and not line_s.startswith("#"):
                    count += 1
                    if "youtube.com" in line_s or "google.com" in line_s:
                        has_youtube = True
        if count > 0:
            yt_tag = " (YouTube session active)" if has_youtube else ""
            return True, count, f"{count} cookies active{yt_tag}"
    except Exception:
        pass
    return False, 0, "Invalid cookies file"

# Regex for parsing yt-dlp progress
# Matches: [download]  12.3% of 45.67MiB at  1.23MiB/s ETA 00:30
# Or: [download]  12.3% of ~45.67MiB at  1.23MiB/s ETA 00:30
YTDLP_PROGRESS_RE = re.compile(r'\[download\]\s+([\d\.]+)%\s+of\s+(?:~\s*)?([^\s]+)\s+at\s+([^\s]+)\s+ETA\s+([^\s]+)')
YTDLP_FINISHED_RE = re.compile(r'\[download\]\s+100%\s+of\s+([^\s]+)\s+in\s+([^\s]+)')

# Regex for parsing aria2c progress
# Matches: [#59c317 11.2MiB/43.6MiB(25%) CN:5 DL:1.2MiB ETA:25s]
ARIA2_PROGRESS_RE = re.compile(r'\[#\w+\s+([^\/]+)\/([^\(]+)\(([\d]+)%\)\s+CN:\d+\s+DL:([^\s]+)\s+ETA:([^\s]+)\]')

# Regex for parsing Instagram URL shortcode
INSTAGRAM_URL_RE = re.compile(r'instagram\.com/(?:p|reel|tv)/([^/?#&]+)', re.IGNORECASE)

class DownloadWorker(QThread):
    progress_updated = pyqtSignal(str, int, str, str, str)  # id, percent, speed, eta, status
    download_completed = pyqtSignal(str, bool, str)        # id, success, error_msg
    log_received = pyqtSignal(str, str)                    # id, log_line

    def __init__(self, download_id, tool_name, tool_path, url, export_dir, profile_settings):
        super().__init__()
        self.download_id = download_id
        self.tool_name = tool_name
        self.tool_path = tool_path
        self.url = url
        self.export_dir = export_dir
        self.settings = profile_settings
        self.process = None
        self._is_cancelled = False
        self.downloaded_files = []

    def run(self):
        try:
            # Build CLI command parameters
            cmd = [self.tool_path]
            
            # Make sure export dir exists
            os.makedirs(self.export_dir, exist_ok=True)
            
            if self.tool_name == "aria2c":
                cmd.append("-d")
                cmd.append(self.export_dir)
                
                # Append connections & split
                connections = self.settings.get("max_connection_per_server", 16)
                split = self.settings.get("split", 16)
                cmd.append(f"-x{connections}")
                cmd.append(f"-s{split}")
                
                # Rate limit
                rate_limit = self.settings.get("max_download_limit", "0")
                if rate_limit and rate_limit != "0":
                    # Append 'K' or 'M' if needed, or if it is already formatted
                    cmd.append(f"--max-download-limit={rate_limit}")
                
                # Add custom flags
                custom_flags = self.settings.get("custom_flags", "")
                if custom_flags:
                    cmd.extend(shlex.split(custom_flags))
                
                # Finally, the URL
                cmd.append(self.url)
                
            elif self.tool_name == "yt-dlp":
                cmd.append("-P")
                cmd.append(self.export_dir)
                
                # Formatting
                fmt = self.settings.get("format", "bestvideo+bestaudio/best")
                cmd.append("-f")
                cmd.append(fmt)
                
                extract_audio = self.settings.get("extract_audio", False)
                # Force audio extraction if format is audio-only to avoid raw opus/webm files
                if fmt.startswith("bestaudio") or ("audio" in fmt.lower() and "video" not in fmt.lower()):
                    extract_audio = True
                
                if extract_audio:
                    cmd.append("-x")
                    audio_fmt = self.settings.get("audio_format", "mp3")
                    # Force compatible audio format for Premiere Pro (mp3, m4a, wav are safe)
                    if audio_fmt not in ["mp3", "m4a", "wav"]:
                        audio_fmt = "mp3"
                    cmd.append("--audio-format")
                    cmd.append(audio_fmt)
                    audio_q = self.settings.get("audio_quality", "5")
                    cmd.append("--audio-quality")
                    cmd.append(audio_q)
                else:
                    video_fmt = self.settings.get("video_format") or self.settings.get("merge_output_format") or "mp4"
                    if video_fmt and video_fmt != "best":
                        cmd.extend(["--merge-output-format", video_fmt])
                        cmd.extend(["--remux-video", video_fmt])
                    
                if self.settings.get("embed_subs", False):
                    cmd.append("--embed-subs")
                
                # YouTube anti-throttling & cache bypass
                cmd.append("--no-cache-dir")
                cmd.append("--geo-bypass")
                
                # Cookie authentication to bypass "Sign in to confirm you're not a bot"
                cookie_source = self.settings.get("cookie_source", "none").lower()
                cookie_file = self.settings.get("cookie_file", "").strip()
                default_root_cookies = os.path.abspath("cookies.txt")

                if cookie_source in ["chrome", "brave", "firefox", "edge", "opera", "vivaldi", "safari"]:
                    cmd.extend(["--cookies-from-browser", cookie_source])
                elif (cookie_source == "custom" or cookie_source == "none") and cookie_file and os.path.exists(cookie_file):
                    cmd.extend(["--cookies", cookie_file])
                elif os.path.exists(default_root_cookies) and os.path.getsize(default_root_cookies) > 0:
                    cmd.extend(["--cookies", default_root_cookies])

                # Optional Proxy configuration
                proxy = self.settings.get("proxy", "").strip()
                if proxy:
                    cmd.extend(["--proxy", proxy])

                # Optional request delay for anti-ban rate limiting
                sleep_req = self.settings.get("sleep_requests", "")
                if sleep_req and str(sleep_req) != "0":
                    cmd.extend(["--sleep-requests", str(sleep_req)])

                # Include local bin folder in PATH and explicitly pass --ffmpeg-location
                env = os.environ.copy()
                bin_dir = os.path.dirname(self.tool_path)
                if os.path.exists(os.path.join(bin_dir, "ffmpeg.exe")):
                    cmd.extend(["--ffmpeg-location", bin_dir])
                if bin_dir not in env.get("PATH", ""):
                    env["PATH"] = bin_dir + os.pathsep + env.get("PATH", "")
                
                # Custom flags
                custom_flags = self.settings.get("custom_flags", "")
                if custom_flags:
                    cmd.extend(shlex.split(custom_flags))
                
                cmd.append(self.url)
                
            elif self.tool_name == "gallery-dl":
                cmd.append("-d")
                cmd.append(self.export_dir)
                
                # Custom flags
                custom_flags = self.settings.get("custom_flags", "")
                if custom_flags:
                    cmd.extend(shlex.split(custom_flags))
                
                cmd.append(self.url)
                
            elif self.tool_name == "spotdl":
                # spotdl uses 'download' command
                cmd.append("download")
                cmd.append(self.url)
                
                # Use --simple-tui for cleaner progress logging
                cmd.append("--simple-tui")
                
                # Add format if specified
                audio_fmt = self.settings.get("audio_format", "mp3")
                cmd.append("--format")
                cmd.append(audio_fmt)
                
                # Add quality/bitrate
                bitrate = self.settings.get("audio_quality", "best")
                cmd.append("--bitrate")
                cmd.append(bitrate)
                
                # Custom flags
                custom_flags = self.settings.get("custom_flags", "")
                if custom_flags:
                    cmd.extend(shlex.split(custom_flags))
                
            elif self.tool_name == "instagram":
                # We execute python module instaloader using python executable:
                # cmd starts with [sys.executable] (from get_tool_path)
                cmd.append("-m")
                cmd.append("instaloader")
                
                # Check for post/reel shortcode in URL
                match = INSTAGRAM_URL_RE.search(self.url)
                if match:
                    shortcode = match.group(1)
                    cmd.append("--")
                    cmd.append(f"-{shortcode}")
                else:
                    # Fallback to username/target extraction
                    user_match = re.search(r'instagram\.com/([^/?#&]+)', self.url)
                    target = user_match.group(1) if user_match else self.url
                    cmd.append(target)
                
                # Options based on settings
                if not self.settings.get("download_pictures", True):
                    cmd.append("--no-pictures")
                if not self.settings.get("download_videos", True):
                    cmd.append("--no-videos")
                if not self.settings.get("download_metadata", False):
                    cmd.append("--no-metadata-json")
                    cmd.append("--no-captions")
                if self.settings.get("download_comments", False):
                    cmd.append("--comments")
                
                # Custom flags
                custom_flags = self.settings.get("custom_flags", "")
                if custom_flags:
                    cmd.extend(shlex.split(custom_flags))
                
            else:
                raise ValueError(f"Unsupported tool: {self.tool_name}")

            # Prepare env if needed
            env = os.environ.copy()
            # Ensure spotdl and yt-dlp can locate ffmpeg
            bin_path = os.path.dirname(self.tool_path)
            if bin_path not in env.get("PATH", ""):
                env["PATH"] = bin_path + os.pathsep + env.get("PATH", "")

            # Log command line to logs pane
            cmd_str = " ".join([f'"{arg}"' if ' ' in arg else arg for arg in cmd])
            self.log_received.emit(self.download_id, f"Executing command: {cmd_str}\n")

            # Spawn subprocess
            cwd_dir = self.export_dir if self.tool_name in ["spotdl", "instagram"] else None
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, # Merge stdout and stderr
                stdin=subprocess.PIPE,    # Sometimes helps to open pipe
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
                cwd=cwd_dir,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            # Read output stream line by line
            while True:
                if self._is_cancelled:
                    self.log_received.emit(self.download_id, "\n[INFO] Download cancelled by user.\n")
                    self.terminate_process()
                    self.download_completed.emit(self.download_id, False, "Cancelled")
                    return
                
                line = self.process.stdout.readline()
                if not line:
                    break
                
                clean_line = line.strip()
                if clean_line:
                    self.log_received.emit(self.download_id, line)
                    self.parse_line_progress(clean_line)
            
            # Wait for exit code
            self.process.wait()
            exit_code = self.process.returncode
            
            if self._is_cancelled:
                self.download_completed.emit(self.download_id, False, "Cancelled")
            elif exit_code == 0:
                # yt-dlp post-processing for Premiere Pro compatibility
                if self.tool_name == "yt-dlp" and not self.settings.get("extract_audio", False):
                    if self.settings.get("premiere_compatible", True):
                        self.process_premiere_compatibility()

                # Instagram post-processing if audio extraction is requested
                if self.tool_name == "instagram":
                    output_type = self.settings.get("output_type", "video_mp4")
                    if output_type in ["audio_m4a", "audio_mp3"]:
                        self.log_received.emit(self.download_id, "\n[INFO] Extracting audio from downloaded Instagram video(s)...\n")
                        # Find all downloaded .mp4 files recursively inside self.export_dir
                        for root, dirs, files in os.walk(self.export_dir):
                            for file in files:
                                if file.lower().endswith(".mp4"):
                                    mp4_path = os.path.join(root, file)
                                    ext = "m4a" if output_type == "audio_m4a" else "mp3"
                                    base_name, _ = os.path.splitext(mp4_path)
                                    audio_path = f"{base_name}.{ext}"
                                    
                                    # Locate ffmpeg.exe in workspace bin folder
                                    ffmpeg_exe = os.path.abspath(os.path.join("bin", "ffmpeg.exe"))
                                    if not os.path.exists(ffmpeg_exe):
                                        ffmpeg_exe = "ffmpeg" # fallback to path
                                        
                                    ffmpeg_cmd = [ffmpeg_exe, "-y", "-i", mp4_path, "-vn"]
                                    if ext == "m4a":
                                        ffmpeg_cmd.extend(["-c:a", "copy", audio_path])
                                    else:
                                        ffmpeg_cmd.extend(["-q:a", "2", audio_path])
                                        
                                    self.log_received.emit(self.download_id, f"Running FFmpeg: {' '.join(ffmpeg_cmd)}\n")
                                    try:
                                        creationflags = 0
                                        if os.name == 'nt':
                                            creationflags = subprocess.CREATE_NO_WINDOW
                                        res = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, creationflags=creationflags)
                                        if res.returncode == 0:
                                            self.log_received.emit(self.download_id, f"Extracted audio: {audio_path}\n")
                                            os.remove(mp4_path)
                                        else:
                                            self.log_received.emit(self.download_id, f"[WARNING] FFmpeg extraction failed: {res.stderr}\n")
                                    except Exception as ex:
                                        self.log_received.emit(self.download_id, f"[WARNING] Failed to run FFmpeg: {str(ex)}\n")

                self.progress_updated.emit(self.download_id, 100, "Done", "0s", "Completed successfully")
                self.download_completed.emit(self.download_id, True, "")
            else:
                self.download_completed.emit(self.download_id, False, f"Process exited with code {exit_code}")

        except Exception as e:
            self.log_received.emit(self.download_id, f"\n[ERROR] Exception occurred: {str(e)}\n")
            self.download_completed.emit(self.download_id, False, str(e))

    def process_premiere_compatibility(self):
        """Checks if downloaded video has AV1/VP9 or Opus and ensures Premiere Pro compatibility."""
        try:
            bin_dir = os.path.dirname(self.tool_path)
            ffmpeg_exe = os.path.join(bin_dir, "ffmpeg.exe")
            if not os.path.exists(ffmpeg_exe):
                ffmpeg_exe = "ffmpeg"
            ffprobe_exe = os.path.join(bin_dir, "ffprobe.exe")
            if not os.path.exists(ffprobe_exe):
                ffprobe_exe = "ffprobe"

            target_file = None
            for f in reversed(self.downloaded_files):
                if os.path.exists(f) and not f.endswith((".part", ".ytdl", ".temp", ".tmp")):
                    target_file = f
                    break

            if not target_file or not os.path.exists(target_file):
                candidates = []
                for root, _, files in os.walk(self.export_dir):
                    for file in files:
                        if file.lower().endswith((".mp4", ".mkv", ".webm", ".mov", ".ts")):
                            full_p = os.path.join(root, file)
                            candidates.append((os.path.getmtime(full_p), full_p))
                if candidates:
                    candidates.sort(reverse=True)
                    target_file = candidates[0][1]

            if not target_file or not os.path.exists(target_file):
                return

            vcodec, acodec, duration = probe_media_codecs(target_file, ffprobe_exe)
            self.log_received.emit(self.download_id, f"\n[INFO] Premiere Pro Compatibility Probe: Video={vcodec}, Audio={acodec}\n")

            prem_vcodecs = ["h264", "hevc", "prores", "dnxhd", "mjpeg"]
            prem_acodecs = ["aac", "mp3", "pcm_s16le", "pcm_s24le", "ac3"]

            needs_video_transcode = vcodec and (vcodec not in prem_vcodecs or vcodec in ["av1", "vp9", "vp8", "av01"])
            needs_audio_transcode = acodec and (acodec not in prem_acodecs or acodec in ["opus", "vorbis", "flac"])

            if not needs_video_transcode and not needs_audio_transcode:
                self.log_received.emit(self.download_id, "[SUCCESS] Media is 100% Premiere Pro ready (H.264 / AAC).\n")
                return

            base_dir = os.path.dirname(target_file)
            base_name = os.path.splitext(os.path.basename(target_file))[0]
            temp_out = os.path.join(base_dir, f"{base_name}_prem_tmp.mp4")
            final_mp4 = os.path.join(base_dir, f"{base_name}.mp4")

            ff_cmd = [ffmpeg_exe, "-y", "-i", target_file]

            if needs_video_transcode:
                enc_args = get_best_h264_encoder_args(ffmpeg_exe)
                self.log_received.emit(self.download_id, f"[INFO] Transcoding {vcodec} to H.264 for Premiere Pro using {' '.join(enc_args)}...\n")
                ff_cmd.extend(enc_args)
            else:
                ff_cmd.extend(["-c:v", "copy"])

            if needs_audio_transcode:
                ff_cmd.extend(["-c:a", "aac", "-b:a", "320k"])
            else:
                ff_cmd.extend(["-c:a", "copy"])

            ff_cmd.extend(["-movflags", "+faststart", temp_out])

            self.log_received.emit(self.download_id, f"Running FFmpeg: {' '.join(ff_cmd)}\n")
            self.progress_updated.emit(self.download_id, 99, "-", "-", "Optimizing for Premiere Pro (H.264/AAC)...")

            creationflags = 0
            if os.name == 'nt':
                creationflags = subprocess.CREATE_NO_WINDOW

            proc = subprocess.Popen(
                ff_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=creationflags
            )

            time_re = re.compile(r'time=(\d+):(\d+):([\d\.]+)')
            speed_re = re.compile(r'speed=\s*([\d\.]+)x')

            while True:
                if self._is_cancelled:
                    proc.kill()
                    if os.path.exists(temp_out):
                        try:
                            os.remove(temp_out)
                        except Exception:
                            pass
                    return

                line = proc.stdout.readline()
                if not line:
                    break

                m_time = time_re.search(line)
                if m_time and duration > 0:
                    hours = int(m_time.group(1))
                    mins = int(m_time.group(2))
                    secs = float(m_time.group(3))
                    cur_sec = hours * 3600 + mins * 60 + secs
                    pct = min(99, max(1, int((cur_sec / duration) * 100)))

                    speed_str = "-"
                    m_speed = speed_re.search(line)
                    if m_speed:
                        speed_str = f"{m_speed.group(1)}x"

                    self.progress_updated.emit(
                        self.download_id, pct, speed_str, "-",
                        f"Premiere Pro Transcode: {pct}%"
                    )

            proc.wait()
            if proc.returncode == 0 and os.path.exists(temp_out):
                try:
                    if os.path.exists(target_file) and os.path.abspath(target_file) != os.path.abspath(final_mp4):
                        os.remove(target_file)
                    elif os.path.exists(final_mp4):
                        os.remove(final_mp4)
                    os.replace(temp_out, final_mp4)
                    self.log_received.emit(self.download_id, f"[SUCCESS] 🎬 File converted to Premiere Pro ready format: {final_mp4}\n")
                except Exception as e:
                    self.log_received.emit(self.download_id, f"[WARNING] Error renaming converted file: {str(e)}\n")
            else:
                self.log_received.emit(self.download_id, f"[WARNING] Premiere Pro transcoding failed with code {proc.returncode}\n")
        except Exception as ex:
            self.log_received.emit(self.download_id, f"[WARNING] Premiere Pro post-processor exception: {str(ex)}\n")

    def cancel(self):
        self._is_cancelled = True
        self.terminate_process()

    def terminate_process(self):
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=3)
            except Exception:
                try:
                    self.process.kill()
                except Exception:
                    pass

    def parse_line_progress(self, line):
        if self.tool_name == "yt-dlp":
            # Track destination or merged file
            if "Destination:" in line:
                dest = line.split("Destination:", 1)[1].strip()
                if dest and not dest.endswith((".part", ".ytdl")):
                    self.downloaded_files.append(dest)
            elif "Merging formats into" in line:
                m = re.search(r'Merging formats into "([^"]+)"', line)
                if m:
                    self.downloaded_files.append(m.group(1))
            elif "Remuxing video" in line:
                m = re.search(r'to "([^"]+)"', line)
                if m:
                    self.downloaded_files.append(m.group(1))
            elif "has already been downloaded" in line:
                m = re.search(r'\[download\] (.+) has already been downloaded', line)
                if m:
                    self.downloaded_files.append(m.group(1).strip())

            # Match downloading state
            match = YTDLP_PROGRESS_RE.match(line)
            if match:
                percent = int(float(match.group(1)))
                size = match.group(2)
                speed = match.group(3)
                eta = match.group(4)
                status = f"Downloading ({size})"
                self.progress_updated.emit(self.download_id, percent, speed, eta, status)
                return
            
            # Match 100% finished state
            match_finished = YTDLP_FINISHED_RE.match(line)
            if match_finished:
                size = match_finished.group(1)
                self.progress_updated.emit(self.download_id, 100, "-", "0s", f"Downloaded ({size})")
                return

            # Special status updates like FFmpeg merging
            if "[ffmpeg]" in line.lower() or "merging formats" in line.lower():
                self.progress_updated.emit(self.download_id, 99, "-", "-", "Post-processing (FFmpeg)...")
                return
                
        elif self.tool_name == "aria2c":
            match = ARIA2_PROGRESS_RE.search(line)
            if match:
                # Group 3 is percent, 4 is speed, 5 is ETA
                percent = int(match.group(3))
                speed = match.group(4) + "/s"
                eta = match.group(5)
                downloaded = match.group(1)
                total = match.group(2)
                status = f"Downloading ({downloaded}/{total})"
                self.progress_updated.emit(self.download_id, percent, speed, eta, status)
                return
                
        elif self.tool_name == "gallery-dl":
            # gallery-dl logs filenames being downloaded. We can show it in status.
            if "[gallery-dl][info]" in line or "downloading" in line.lower():
                # Display dynamic status line
                parts = line.split("Downloading")
                filename = parts[-1].strip() if len(parts) > 1 else ""
                status_msg = f"Downloading {filename}" if filename else "Downloading gallery..."
                self.progress_updated.emit(self.download_id, -1, "-", "-", status_msg)
                return

        elif self.tool_name == "spotdl":
            # Parse percentage (e.g., 45% or 45.2%)
            match = re.search(r'(\d+)%', line)
            if match:
                percent = int(match.group(1))
                speed = "-"
                eta = "-"
                
                # Check for speed, e.g., "0.5MB/s"
                speed_match = re.search(r'([\d\.]+[KkMm]B/s)', line)
                if speed_match:
                    speed = speed_match.group(1)
                    
                # Check for ETA, e.g., "ETA: 00:03" or "ETA 00:03"
                eta_match = re.search(r'ETA[\s:]+([^\], ]+)', line)
                if eta_match:
                    eta = eta_match.group(1)
                    
                self.progress_updated.emit(self.download_id, percent, speed, eta, "Downloading Spotify track...")
                return
                
            if "lookup" in line.lower() or "searching" in line.lower():
                self.progress_updated.emit(self.download_id, 5, "-", "-", "Searching Spotify metadata...")
                return
            elif "converting" in line.lower() or "ffmpeg" in line.lower() or "encoding" in line.lower() or "mbedding" in line.lower():
                self.progress_updated.emit(self.download_id, 95, "-", "-", "Post-processing (FFmpeg)...")
                return

        elif self.tool_name == "instagram":
            line_lower = line.lower()
            if "retrieving" in line_lower:
                self.progress_updated.emit(self.download_id, 10, "-", "-", "Retrieving Instagram target...")
                return
            elif ".mp4" in line_lower:
                self.progress_updated.emit(self.download_id, 50, "-", "-", "Downloading Instagram video...")
                return
            elif ".jpg" in line_lower or ".png" in line_lower or ".webp" in line_lower:
                self.progress_updated.emit(self.download_id, 80, "-", "-", "Downloading Instagram pictures...")
                return
            elif "downloading" in line_lower or "saving" in line_lower:
                # Extract filename if visible
                parts = line.split(" ")
                target = parts[-1].strip() if parts else ""
                self.progress_updated.emit(self.download_id, 30, "-", "-", f"Downloading {target}" if target else "Downloading Instagram post...")
                return
