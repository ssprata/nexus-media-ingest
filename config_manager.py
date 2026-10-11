import os
import re
import json
from datetime import datetime

DEFAULT_CONFIG_PATH = "config.json"
DEFAULT_EXPORT_DIR = os.path.normpath(os.path.join(os.path.expanduser("~/Downloads"), "Nexus Ingest"))

def sanitize_path_component(name):
    if not name:
        return ""
    sanitized = re.sub(r'[\\/:*?"<>|]', '_', str(name)).strip()
    return sanitized.strip('. ')

DEFAULT_PROFILES = [
    {
        "name": "Default Direct (aria2c)",
        "tool": "aria2c",
        "folder": "Nexus Ingest",
        "use_custom_path": False,
        "export_dir": DEFAULT_EXPORT_DIR,
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
        "folder": "Nexus Ingest",
        "use_custom_path": False,
        "export_dir": DEFAULT_EXPORT_DIR,
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
        "folder": "Nexus Ingest",
        "use_custom_path": False,
        "export_dir": DEFAULT_EXPORT_DIR,
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
        "folder": "Nexus Ingest",
        "use_custom_path": False,
        "export_dir": DEFAULT_EXPORT_DIR,
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
        "folder": "Nexus Ingest",
        "use_custom_path": False,
        "export_dir": DEFAULT_EXPORT_DIR,
        "spotdl_settings": {
            "audio_format": "mp3",
            "audio_quality": "auto",
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
        "folder": "Nexus Ingest",
        "use_custom_path": False,
        "export_dir": DEFAULT_EXPORT_DIR,
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
            "main_library_dir": DEFAULT_EXPORT_DIR,
            "profiles": DEFAULT_PROFILES
        }
        self.load()

    def load(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if "main_library_dir" in loaded and loaded["main_library_dir"]:
                        self.config["main_library_dir"] = os.path.normpath(loaded["main_library_dir"])
                    else:
                        self.config["main_library_dir"] = DEFAULT_EXPORT_DIR

                    if "profiles" in loaded:
                        self.config["profiles"] = loaded["profiles"]
                        # Ensure every profile has folder, use_custom_path, and proper normalization
                        for p in self.config["profiles"]:
                            if "folder" not in p:
                                p["folder"] = ""
                            if "use_custom_path" not in p:
                                curr_dir = p.get("export_dir", "")
                                # If existing config already had an explicit path, maintain custom flag
                                p["use_custom_path"] = bool(curr_dir and os.path.normpath(curr_dir) != DEFAULT_EXPORT_DIR)

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
                    self.config["max_concurrent_downloads"] = loaded.get("max_concurrent_downloads", 2)
                    self.config["enable_animations"] = loaded.get("enable_animations", True)
                    self.config["clipboard_sniffer"] = loaded.get("clipboard_sniffer", False)
                    self.config["global_speed_limit"] = loaded.get("global_speed_limit", "0")
            except Exception as e:
                print(f"Error loading config: {e}. Resetting to defaults.")
                self.save()
        else:
            self.config["main_library_dir"] = DEFAULT_EXPORT_DIR
            self.config["max_concurrent_downloads"] = 2
            self.config["enable_animations"] = True
            self.config["clipboard_sniffer"] = False
            self.config["global_speed_limit"] = "0"
            self.save()

    def save(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    # --- Main Library Directory & Relative Paths ---
    def get_main_library_dir(self):
        dir_path = self.config.get("main_library_dir") or DEFAULT_EXPORT_DIR
        return os.path.normpath(dir_path)

    def set_main_library_dir(self, dir_path):
        clean_path = os.path.normpath(dir_path.strip()) if dir_path else DEFAULT_EXPORT_DIR
        self.config["main_library_dir"] = clean_path
        self.save()
        try:
            os.makedirs(clean_path, exist_ok=True)
        except Exception as e:
            print(f"Error creating main library directory {clean_path}: {e}")
        return clean_path

    def resolve_profile_export_dir(self, profile):
        """Resolves target folder on disk. If use_custom_path is True, returns export_dir.
        Otherwise dynamically returns {main_library_dir}/{folder}/{profile_name}."""
        if profile.get("use_custom_path", False) and profile.get("export_dir"):
            return os.path.normpath(profile.get("export_dir"))

        main_dir = self.get_main_library_dir()
        folder = sanitize_path_component(profile.get("folder", "") or "")
        name = sanitize_path_component(profile.get("name", "") or "Default")

        if folder:
            target = os.path.join(main_dir, folder, name)
        else:
            target = os.path.join(main_dir, name)
        return os.path.normpath(target)

    def ensure_profile_export_dir(self, profile):
        """Resolves target directory and ensures it physically exists on disk."""
        target_dir = self.resolve_profile_export_dir(profile)
        try:
            os.makedirs(target_dir, exist_ok=True)
        except Exception as e:
            print(f"Error ensuring directory {target_dir}: {e}")
        return target_dir

    def ensure_folder_dir(self, folder_name):
        """Ensures a category folder exists on disk inside the main library."""
        folder = sanitize_path_component(folder_name)
        if not folder:
            return self.get_main_library_dir()
        target = os.path.normpath(os.path.join(self.get_main_library_dir(), folder))
        try:
            os.makedirs(target, exist_ok=True)
        except Exception as e:
            print(f"Error creating folder {target}: {e}")
        return target

    # --- Profiles Management ---
    def get_profiles(self):
        return self.config["profiles"]

    def get_active_profile_name(self):
        return self.config.get("active_profile")

    def get_active_profile(self):
        active_name = self.get_active_profile_name()
        for p in self.config["profiles"]:
            if p["name"] == active_name:
                return p
        if self.config["profiles"]:
            self.config["active_profile"] = self.config["profiles"][0]["name"]
            self.save()
            return self.config["profiles"][0]
        return None

    def set_active_profile(self, name):
        self.config["active_profile"] = name
        self.save()

    def add_profile(self, profile):
        if "use_custom_path" not in profile:
            profile["use_custom_path"] = False
        self.config["profiles"].append(profile)
        self.ensure_profile_export_dir(profile)
        self.save()

    def update_profile(self, name, updated_profile):
        for idx, p in enumerate(self.config["profiles"]):
            if p["name"] == name:
                self.config["profiles"][idx] = updated_profile
                if name == self.config["active_profile"]:
                    self.config["active_profile"] = updated_profile["name"]
                self.ensure_profile_export_dir(updated_profile)
                self.save()
                return True
        return False

    def delete_profile(self, name):
        if len(self.config["profiles"]) <= 1:
            return False
        
        self.config["profiles"] = [p for p in self.config["profiles"] if p["name"] != name]
        
        if self.config["active_profile"] == name:
            self.config["active_profile"] = self.config["profiles"][0]["name"]
        
        self.save()
        return True

    # --- Portable Export & Import ---
    def export_profiles(self, export_file_path, scope="all", scope_target=None):
        """Exports profiles into a portable JSON package."""
        all_profiles = self.get_profiles()
        if scope == "profile" and scope_target:
            to_export = [p for p in all_profiles if p.get("name") == scope_target]
        elif scope == "folder" and scope_target:
            to_export = [p for p in all_profiles if p.get("folder") == scope_target]
        else:
            scope = "all"
            to_export = list(all_profiles)

        if not to_export:
            return False, "No matching profiles found to export."

        package_data = {
            "nexus_package": True,
            "format_version": "1.0",
            "exported_at": datetime.now().isoformat(),
            "scope": scope,
            "scope_target": scope_target or "All Profiles",
            "profile_count": len(to_export),
            "profiles": to_export
        }

        try:
            with open(export_file_path, "w", encoding="utf-8") as f:
                json.dump(package_data, f, indent=4)
            return True, f"Successfully exported {len(to_export)} profile(s) to '{os.path.basename(export_file_path)}'."
        except Exception as e:
            return False, f"Failed to save export file: {str(e)}"

    def import_profiles(self, import_file_path, mode="merge"):
        """Imports profiles from a JSON / .nexus package."""
        if not os.path.exists(import_file_path):
            return False, "File does not exist."

        try:
            with open(import_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            return False, f"Invalid JSON file: {str(e)}"

        incoming = []
        if isinstance(data, dict) and "profiles" in data and isinstance(data["profiles"], list):
            incoming = data["profiles"]
        elif isinstance(data, list):
            incoming = data
        else:
            return False, "Unrecognized format. Expected a Nexus profile bundle."

        cleaned_incoming = []
        for p in incoming:
            if not isinstance(p, dict) or "name" not in p or "tool" not in p:
                continue
            p_copy = dict(p)
            if "folder" not in p_copy:
                p_copy["folder"] = ""
            if "use_custom_path" not in p_copy:
                p_copy["use_custom_path"] = False
            cleaned_incoming.append(p_copy)

        if not cleaned_incoming:
            return False, "No valid profiles found in import file."

        if mode == "replace":
            self.config["profiles"] = cleaned_incoming
            self.config["active_profile"] = cleaned_incoming[0]["name"]
        else:  # merge mode
            existing_names = set(p["name"] for p in self.config["profiles"])
            for p in cleaned_incoming:
                orig_name = p["name"]
                new_name = orig_name
                idx = 1
                while new_name in existing_names:
                    new_name = f"{orig_name} (Imported {idx})"
                    idx += 1
                p["name"] = new_name
                existing_names.add(new_name)
                self.config["profiles"].append(p)

        # Pre-create disk directories for imported profiles
        for p in self.config["profiles"]:
            self.ensure_profile_export_dir(p)

        self.save()
        return True, f"Successfully imported {len(cleaned_incoming)} profile(s) ({mode} mode)."

    def get_max_concurrent_downloads(self):
        return int(self.config.get("max_concurrent_downloads", 2))

    def set_max_concurrent_downloads(self, val):
        self.config["max_concurrent_downloads"] = max(1, min(10, int(val)))
        self.save()

    def get_enable_animations(self):
        return bool(self.config.get("enable_animations", True))

    def set_enable_animations(self, val):
        self.config["enable_animations"] = bool(val)
        self.save()

    def get_clipboard_sniffer(self):
        return bool(self.config.get("clipboard_sniffer", False))

    def set_clipboard_sniffer(self, val):
        self.config["clipboard_sniffer"] = bool(val)
        self.save()

    def get_global_speed_limit(self):
        return str(self.config.get("global_speed_limit", "0"))

    def set_global_speed_limit(self, val):
        self.config["global_speed_limit"] = str(val).strip()
        self.save()
