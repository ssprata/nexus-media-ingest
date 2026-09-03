import os
import json

DEFAULT_CONFIG_PATH = "config.json"

DEFAULT_PROFILES = [
    {
        "name": "Default Direct (aria2c)",
        "tool": "aria2c",
        "folder": "",
        "export_dir": os.path.expanduser("~/Downloads"),
        "aria2_settings": {
            "max_connection_per_server": 16,
            "split": 16,
            "max_download_limit": "0",
            "custom_flags": ""
        },
        "ytdlp_settings": {},
        "gallerydl_settings": {},
        "spotdl_settings": {},
        "instagram_settings": {}
    },
    {
        "name": "YouTube Video (yt-dlp)",
        "tool": "yt-dlp",
        "folder": "",
        "export_dir": os.path.expanduser("~/Downloads"),
        "ytdlp_settings": {
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
            "video_format": "mp4",
            "extract_audio": False,
            "embed_subs": True,
            "premiere_compatible": True,
            "cookie_source": "none",
            "cookie_file": "",
            "proxy": "",
            "sleep_requests": "",
            "custom_flags": ""
        },
        "aria2_settings": {},
        "gallerydl_settings": {},
        "spotdl_settings": {},
        "instagram_settings": {}
    },
    {
        "name": "YouTube Music (yt-dlp)",
        "tool": "yt-dlp",
        "folder": "",
        "export_dir": os.path.expanduser("~/Downloads"),
        "ytdlp_settings": {
            "format": "bestaudio/best",
            "extract_audio": True,
            "audio_format": "mp3",
            "audio_quality": "5",
            "custom_flags": ""
        },
        "aria2_settings": {},
        "gallerydl_settings": {},
        "spotdl_settings": {},
        "instagram_settings": {}
    },
    {
        "name": "Image Galleries (gallery-dl)",
        "tool": "gallery-dl",
        "folder": "",
        "export_dir": os.path.expanduser("~/Downloads"),
        "gallerydl_settings": {
            "custom_flags": ""
        },
        "aria2_settings": {},
        "ytdlp_settings": {},
        "spotdl_settings": {},
        "instagram_settings": {}
    },
    {
        "name": "Spotify Download (spotdl)",
        "tool": "spotdl",
        "folder": "",
        "export_dir": os.path.expanduser("~/Downloads"),
        "spotdl_settings": {
            "audio_format": "mp3",
            "audio_quality": "best",
            "custom_flags": ""
        },
        "aria2_settings": {},
        "ytdlp_settings": {},
        "gallerydl_settings": {},
        "instagram_settings": {}
    },
    {
        "name": "Instagram Post/Reel (instaloader)",
        "tool": "instagram",
        "folder": "",
        "export_dir": os.path.expanduser("~/Downloads"),
        "instagram_settings": {
            "download_pictures": True,
            "download_videos": True,
            "download_metadata": False,
            "download_comments": False,
            "output_type": "video_mp4",
            "custom_flags": ""
        },
        "aria2_settings": {},
        "ytdlp_settings": {},
        "gallerydl_settings": {},
        "spotdl_settings": {}
    }
]

class ConfigManager:
    def __init__(self, config_path=DEFAULT_CONFIG_PATH):
        self.config_path = config_path
        self.config = {
            "active_profile": "Default Direct (aria2c)",
            "profiles": DEFAULT_PROFILES
        }
        self.load()

    def load(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if "profiles" in loaded:
                        self.config["profiles"] = loaded["profiles"]
                        # Ensure every profile has a folder key and normalization
                        for p in self.config["profiles"]:
                            if "folder" not in p:
                                p["folder"] = ""
                            if "spotdl_settings" not in p or not isinstance(p["spotdl_settings"], dict):
                                p["spotdl_settings"] = {
                                    "audio_format": "mp3",
                                    "audio_quality": "best",
                                    "custom_flags": ""
                                }
                            if "instagram_settings" not in p or not isinstance(p["instagram_settings"], dict):
                                p["instagram_settings"] = {
                                    "download_pictures": True,
                                    "download_videos": True,
                                    "download_metadata": False,
                                    "download_comments": False,
                                    "output_type": "video_mp4",
                                    "custom_flags": ""
                                }
                            else:
                                if "output_type" not in p["instagram_settings"]:
                                    p["instagram_settings"]["output_type"] = "video_mp4"
                            if "ytdlp_settings" in p and isinstance(p["ytdlp_settings"], dict):
                                if "video_format" not in p["ytdlp_settings"]:
                                    p["ytdlp_settings"]["video_format"] = p["ytdlp_settings"].get("merge_output_format", "best")
                    if "active_profile" in loaded:
                        self.config["active_profile"] = loaded["active_profile"]
            except Exception as e:
                print(f"Error loading config: {e}. Resetting to defaults.")
                self.save()
        else:
            self.save()

    def save(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get_profiles(self):
        return self.config["profiles"]

    def get_active_profile_name(self):
        return self.config.get("active_profile")

    def get_active_profile(self):
        active_name = self.get_active_profile_name()
        for p in self.config["profiles"]:
            if p["name"] == active_name:
                return p
        # Fallback if active profile is missing
        if self.config["profiles"]:
            self.config["active_profile"] = self.config["profiles"][0]["name"]
            self.save()
            return self.config["profiles"][0]
        return None

    def set_active_profile(self, name):
        self.config["active_profile"] = name
        self.save()

    def add_profile(self, profile):
        self.config["profiles"].append(profile)
        self.save()

    def update_profile(self, name, updated_profile):
        for idx, p in enumerate(self.config["profiles"]):
            if p["name"] == name:
                self.config["profiles"][idx] = updated_profile
                # If we renamed the active profile, update active_profile field
                if name == self.config["active_profile"]:
                    self.config["active_profile"] = updated_profile["name"]
                self.save()
                return True
        return False

    def delete_profile(self, name):
        # Prevent deleting the last profile
        if len(self.config["profiles"]) <= 1:
            return False
        
        self.config["profiles"] = [p for p in self.config["profiles"] if p["name"] != name]
        
        if self.config["active_profile"] == name:
            self.config["active_profile"] = self.config["profiles"][0]["name"]
        
        self.save()
        return True
