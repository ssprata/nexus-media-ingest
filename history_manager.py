import os
import json
import time
from datetime import datetime

DEFAULT_HISTORY_FILE = "history.json"

def format_size(bytes_size):
    if not bytes_size or bytes_size <= 0:
        return "-"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

class HistoryManager:
    def __init__(self, file_path=DEFAULT_HISTORY_FILE):
        self.file_path = file_path
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.file_path):
            try:
                with open(self.file_path, "w", encoding="utf-8") as f:
                    json.dump([], f, indent=2)
            except Exception:
                pass

    def load_records(self):
        self._ensure_file()
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception:
            return []

    def save_records(self, records):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2)
        except Exception as e:
            print(f"Failed to save history: {e}")

    def add_record(self, download_id, url, tool, status, export_dir, file_path="", error_msg=""):
        records = self.load_records()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        file_size_str = "-"
        title = ""
        if file_path and os.path.exists(file_path):
            try:
                size_bytes = os.path.getsize(file_path)
                file_size_str = format_size(size_bytes)
                title = os.path.basename(file_path)
            except Exception:
                pass

        if not title:
            # Fallback title from url
            title = url.split("?")[0].split("/")[-1] or url

        record = {
            "id": download_id,
            "timestamp": now_str,
            "url": url,
            "tool": tool,
            "status": status,
            "export_dir": export_dir,
            "file_path": file_path,
            "file_size": file_size_str,
            "title": title,
            "error_msg": error_msg
        }

        # Keep newest first, limit to 500 records
        records.insert(0, record)
        if len(records) > 500:
            records = records[:500]

        self.save_records(records)
        return record

    def delete_record(self, record_id):
        records = self.load_records()
        records = [r for r in records if r.get("id") != record_id]
        self.save_records(records)

    def clear_history(self):
        self.save_records([])
