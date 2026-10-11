import os
import subprocess
import uuid
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode
from PyQt6.QtCore import Qt, pyqtSignal, QThread, pyqtSlot, QTimer, QPropertyAnimation, QEasingCurve, QUrl, QRectF
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPlainTextEdit, QPushButton, QListWidget,
    QComboBox, QProgressBar, QTabWidget, QSpinBox, QCheckBox,
    QFileDialog, QMessageBox, QSplitter, QScrollArea, QFrame,
    QSizePolicy, QFormLayout, QGroupBox, QDialog, QTreeWidget, QTreeWidgetItem,
    QApplication, QTableWidget, QTableWidgetItem, QHeaderView, QSystemTrayIcon, QMenu,
    QGraphicsOpacityEffect, QGraphicsDropShadowEffect
)
import json
import requests
from PyQt6.QtGui import (
    QColor, QFont, QClipboard, QIcon, QPixmap, QDesktopServices,
    QPainter, QBrush, QLinearGradient, QPen, QPainterPath
)

from config_manager import ConfigManager
from dependency_manager import DependencyManager
from downloader import DownloadWorker
from history_manager import HistoryManager


class CyberMessageBox(QDialog):
    def __init__(self, title, message, is_confirm=False, border_color="#ff007f", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        
        self.setObjectName("card_frame")
        self.setStyleSheet(f"""
            QDialog#card_frame {{
                background-color: #04050a;
                border: 2px solid {border_color};
                border-radius: 12px;
            }}
        """)
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(220)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.start()
        self.setup_ui(title, message, is_confirm, border_color)

    def setup_ui(self, title, message, is_confirm, border_color):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(18)

        title_lbl = QLabel(title.upper())
        title_lbl.setStyleSheet(f"font-size: 15px; font-weight: 800; color: {border_color}; letter-spacing: 1px;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_lbl)

        msg_lbl = QLabel(message)
        msg_lbl.setStyleSheet("font-size: 13px; color: #e2e8f0; line-height: 1.4;")
        msg_lbl.setWordWrap(True)
        msg_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(msg_lbl)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        if is_confirm:
            yes_btn = QPushButton("CONFIRM")
            yes_btn.setObjectName("neon_cyan_btn")
            yes_btn.clicked.connect(self.accept)
            
            no_btn = QPushButton("CANCEL")
            no_btn.setObjectName("neon_magenta_btn")
            no_btn.clicked.connect(self.reject)
            
            btn_layout.addStretch()
            btn_layout.addWidget(yes_btn)
            btn_layout.addWidget(no_btn)
            btn_layout.addStretch()
        else:
            ok_btn = QPushButton("OK")
            if border_color == "#00f0ff":
                ok_btn.setObjectName("neon_cyan_btn")
            else:
                ok_btn.setObjectName("neon_magenta_btn")
            ok_btn.setFixedWidth(120)
            ok_btn.clicked.connect(self.accept)
            
            btn_layout.addStretch()
            btn_layout.addWidget(ok_btn)
            btn_layout.addStretch()

        layout.addLayout(btn_layout)

    @staticmethod
    def show_info(parent, title, message, border_color="#00f0ff"):
        dialog = CyberMessageBox(title, message, is_confirm=False, border_color=border_color, parent=parent)
        if parent:
            dialog.adjustSize()
            geom = parent.geometry()
            x = geom.x() + (geom.width() - dialog.width()) // 2
            y = geom.y() + (geom.height() - dialog.height()) // 2
            dialog.move(x, y)
        dialog.exec()

    @staticmethod
    def show_question(parent, title, message, border_color="#ff007f"):
        dialog = CyberMessageBox(title, message, is_confirm=True, border_color=border_color, parent=parent)
        if parent:
            dialog.adjustSize()
            geom = parent.geometry()
            x = geom.x() + (geom.width() - dialog.width()) // 2
            y = geom.y() + (geom.height() - dialog.height()) // 2
            dialog.move(x, y)
        return dialog.exec() == QDialog.DialogCode.Accepted


class CyberInputDialog(QDialog):
    def __init__(self, title, label_text, default_value="", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        
        self.setObjectName("card_frame")
        self.setStyleSheet("""
            QDialog#card_frame {
                background-color: #04050a;
                border: 2px solid #00f0ff;
                border-radius: 12px;
            }
        """)
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(220)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.start()
        self.value = ""
        self.setup_ui(title, label_text, default_value)

    def setup_ui(self, title, label_text, default_value):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        title_lbl = QLabel(title.upper())
        title_lbl.setStyleSheet("font-size: 15px; font-weight: 800; color: #00f0ff; letter-spacing: 1px;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_lbl)

        label = QLabel(label_text)
        label.setStyleSheet("font-size: 13px; color: #e2e8f0;")
        layout.addWidget(label)

        self.input_edit = QLineEdit(default_value)
        layout.addWidget(self.input_edit)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        ok_btn = QPushButton("CONFIRM")
        ok_btn.setObjectName("neon_cyan_btn")
        ok_btn.clicked.connect(self.on_ok_clicked)

        cancel_btn = QPushButton("CANCEL")
        cancel_btn.setObjectName("neon_magenta_btn")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

    def on_ok_clicked(self):
        self.value = self.input_edit.text().strip()
        self.accept()

    @staticmethod
    def get_text(parent, title, label_text, default_value=""):
        dialog = CyberInputDialog(title, label_text, default_value, parent=parent)
        if parent:
            dialog.adjustSize()
            geom = parent.geometry()
            x = geom.x() + (geom.width() - dialog.width()) // 2
            y = geom.y() + (geom.height() - dialog.height()) // 2
            dialog.move(x, y)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.value, True
        return "", False


class CyberChoiceDialog(QDialog):
    def __init__(self, title, message, opt1_text="Merge", opt2_text="Replace", cancel_text="Cancel", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        
        self.setObjectName("card_frame")
        self.setStyleSheet("""
            QDialog#card_frame {
                background-color: #04050a;
                border: 2px solid #00f0ff;
                border-radius: 12px;
            }
        """)
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(220)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.start()

        self.selected_choice = None
        self.setup_ui(title, message, opt1_text, opt2_text, cancel_text)

    def setup_ui(self, title, message, opt1_text, opt2_text, cancel_text):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(16)

        title_lbl = QLabel(title.upper())
        title_lbl.setStyleSheet("font-size: 15px; font-weight: 800; color: #00f0ff; letter-spacing: 1px;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_lbl)

        msg_lbl = QLabel(message)
        msg_lbl.setStyleSheet("font-size: 13px; color: #e2e8f0; line-height: 1.4;")
        msg_lbl.setWordWrap(True)
        msg_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(msg_lbl)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        b1 = QPushButton(opt1_text)
        b1.setObjectName("neon_cyan_btn")
        b1.clicked.connect(lambda: self.choose(opt1_text.lower()))

        b2 = QPushButton(opt2_text)
        b2.setObjectName("neon_purple_btn")
        b2.clicked.connect(lambda: self.choose(opt2_text.lower()))

        bc = QPushButton(cancel_text)
        bc.setObjectName("neon_magenta_btn")
        bc.clicked.connect(lambda: self.choose(None))

        btn_layout.addWidget(b1)
        btn_layout.addWidget(b2)
        btn_layout.addWidget(bc)
        layout.addLayout(btn_layout)

    def choose(self, choice):
        self.selected_choice = choice
        self.accept()

    @staticmethod
    def get_choice(parent, title, message, opt1_text="Merge", opt2_text="Replace"):
        dialog = CyberChoiceDialog(title, message, opt1_text, opt2_text, parent=parent)
        if parent:
            dialog.adjustSize()
            geom = parent.geometry()
            x = geom.x() + (geom.width() - dialog.width()) // 2
            y = geom.y() + (geom.height() - dialog.height()) // 2
            dialog.move(x, y)
        dialog.exec()
        return dialog.selected_choice


def inspect_youtube_url(url):
    """
    Analyzes a URL to see if it is a YouTube video inside an attached playlist or mix.
    Returns: (is_yt, has_playlist, is_mix, is_pure_playlist, single_url)
    """
    u_lower = url.lower().strip()
    if "youtube.com" not in u_lower and "youtu.be" not in u_lower:
        return False, False, False, False, url
    if "list=" not in url:
        return True, False, False, False, url
    try:
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        list_ids = qs.get("list", [])
        if not list_ids:
            return True, False, False, False, url
        list_id = list_ids[0]
        is_mix = list_id.startswith("RD")
        has_video = "v" in qs or "youtu.be" in parsed.netloc
        is_pure_playlist = not has_video and (parsed.path == "/playlist" or "playlist" in parsed.path)

        if has_video:
            clean_params = {k: v for k, v in qs.items() if k not in ["list", "index", "start_radio"]}
            new_query = urlencode(clean_params, doseq=True)
            single_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))
            return True, True, is_mix, False, single_url
        else:
            return True, True, is_mix, is_pure_playlist, url
    except Exception:
        return True, False, False, False, url


class CyberPlaylistDialog(QDialog):
    CHOICE_SINGLE = "single"
    CHOICE_PLAYLIST = "playlist"
    CHOICE_CANCEL = "cancel"

    def __init__(self, url, is_mix=False, parent=None):
        super().__init__(parent)
        self.url = url
        self.is_mix = is_mix
        self.choice = self.CHOICE_SINGLE
        self.apply_to_all = False

        self.setWindowTitle("YouTube Mix / Playlist Detected")
        self.setModal(True)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setMinimumWidth(540)

        self.setObjectName("card_frame")
        self.setStyleSheet("""
            QDialog#card_frame {
                background-color: #04050a;
                border: 2px solid #00f0ff;
                border-radius: 12px;
            }
        """)

        # Smooth entrance fade-in animation
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(220)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.start()

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(16)

        # Header Title
        type_str = "🔀 YOUTUBE MIX DETECTED" if self.is_mix else "📑 YOUTUBE PLAYLIST DETECTED"
        title_lbl = QLabel(type_str)
        title_lbl.setStyleSheet("font-size: 15px; font-weight: 800; color: #00f0ff; letter-spacing: 1px;")
        layout.addWidget(title_lbl)

        # Explanation
        desc_text = (
            "The link you entered is part of a <b>YouTube Mix</b> (radio queue).<br>"
            "YouTube mixes usually contain <b>50+ songs</b>. Did you want to ingest only this single song, or the full mix?"
            if self.is_mix else
            "The link you entered contains a <b>single video</b> inside an attached <b>playlist</b>.<br>"
            "Would you like to ingest <b>only the single song/video</b>, or the entire playlist?"
        )
        desc_lbl = QLabel(desc_text)
        desc_lbl.setStyleSheet("color: #cbd5e1; font-size: 13px; line-height: 1.45;")
        desc_lbl.setWordWrap(True)
        layout.addWidget(desc_lbl)

        # URL Preview Chip
        url_box = QFrame()
        url_box.setStyleSheet("background-color: #080912; border: 1px solid #1a1e32; border-radius: 6px; padding: 6px 10px;")
        ub_layout = QVBoxLayout(url_box)
        disp_url = self.url if len(self.url) <= 75 else self.url[:72] + "..."
        u_lbl = QLabel(disp_url)
        u_lbl.setStyleSheet("color: #38bdf8; font-family: 'JetBrains Mono', Consolas, monospace; font-size: 11px;")
        u_lbl.setWordWrap(True)
        ub_layout.addWidget(u_lbl)
        layout.addWidget(url_box)

        # Apply to all checkbox
        self.apply_all_cb = QCheckBox("Apply this decision to all remaining playlist/mix links in this batch")
        self.apply_all_cb.setStyleSheet("color: #94a3b8; font-size: 12px;")
        layout.addWidget(self.apply_all_cb)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.single_btn = QPushButton("🎵 Single Song Only (Recommended)")
        self.single_btn.setStyleSheet("""
            QPushButton {
                background: #00f0ff;
                color: #000000;
                border: 1px solid #00f0ff;
                font-weight: 800;
                padding: 9px 14px;
                border-radius: 7px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #38bdf8;
                border-color: #ffffff;
            }
        """)
        self.single_btn.clicked.connect(self.on_single_clicked)
        btn_layout.addWidget(self.single_btn)

        self.playlist_btn = QPushButton("📑 Full Playlist / Mix")
        self.playlist_btn.setObjectName("neon_purple_btn")
        self.playlist_btn.clicked.connect(self.on_playlist_clicked)
        btn_layout.addWidget(self.playlist_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("neon_magenta_btn")
        cancel_btn.clicked.connect(self.on_cancel_clicked)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def on_single_clicked(self):
        self.choice = self.CHOICE_SINGLE
        self.apply_to_all = self.apply_all_cb.isChecked()
        self.accept()

    def on_playlist_clicked(self):
        self.choice = self.CHOICE_PLAYLIST
        self.apply_to_all = self.apply_all_cb.isChecked()
        self.accept()

    def on_cancel_clicked(self):
        self.choice = self.CHOICE_CANCEL
        self.apply_to_all = self.apply_all_cb.isChecked()
        self.reject()


class CookieManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("YouTube Cookie & Bot-Bypass Manager")
        self.setMinimumWidth(560)
        self.setMinimumHeight(440)
        self.setObjectName("card_frame")
        self.setStyleSheet("""
            QDialog#card_frame {
                background-color: #04050a;
                border: 2px solid #00f0ff;
                border-radius: 12px;
            }
            QLabel {
                color: #cbd5e1;
            }
            QPlainTextEdit {
                background-color: #0d0f18;
                color: #38bdf8;
                border: 1px solid #334155;
                border-radius: 6px;
                font-family: Consolas, monospace;
                font-size: 11px;
            }
        """)
        self.setup_ui()
        self.update_status()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Title
        title_lbl = QLabel("🍪 YOUTUBE COOKIE & BOT-BYPASS MANAGER")
        title_lbl.setStyleSheet("font-size: 15px; font-weight: 800; color: #00f0ff; letter-spacing: 1px;")
        layout.addWidget(title_lbl)

        # Status Card
        self.status_box = QFrame()
        self.status_box.setStyleSheet("background-color: #16192b; border: 1px solid #00f0ff; border-radius: 8px; padding: 10px;")
        sb_layout = QHBoxLayout(self.status_box)
        self.status_icon_lbl = QLabel("🟢")
        self.status_text_lbl = QLabel("Checking cookie status...")
        self.status_text_lbl.setStyleSheet("font-size: 12px; font-weight: bold; color: #10b981;")
        sb_layout.addWidget(self.status_icon_lbl)
        sb_layout.addWidget(self.status_text_lbl, 1)
        
        self.clear_cookies_btn = QPushButton("🗑 Clear Cookies")
        self.clear_cookies_btn.setStyleSheet("background-color: #471323; color: #ff007f; border: 1px solid #ff007f; border-radius: 5px; padding: 4px 10px; font-size: 11px;")
        self.clear_cookies_btn.clicked.connect(self.on_clear_cookies)
        sb_layout.addWidget(self.clear_cookies_btn)
        layout.addWidget(self.status_box)

        # Tabs for methods
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #1e293b; background-color: #121420; border-radius: 6px; }
            QTabBar::tab { background-color: #0f172a; color: #94a3b8; padding: 8px 14px; margin-right: 2px; }
            QTabBar::tab:selected { background-color: #1e293b; color: #00f0ff; font-weight: bold; }
        """)

        # TAB 1: Paste Cookies (Recommended)
        paste_tab = QWidget()
        pt_layout = QVBoxLayout(paste_tab)
        pt_layout.setContentsMargins(14, 14, 14, 14)
        pt_layout.setSpacing(10)

        ext_row = QHBoxLayout()
        pt_info = QLabel("<b>RECOMMENDED (100% RELIABLE):</b> Export cookies from YouTube in your browser:")
        pt_info.setStyleSheet("color: #00f0ff; font-size: 12px;")
        ext_row.addWidget(pt_info, 1)

        self.get_ext_btn = QPushButton("🌐 Get Extension (Chrome Web Store)")
        self.get_ext_btn.setStyleSheet("background-color: #fbbf24; color: #000; font-weight: bold; padding: 6px 12px; border-radius: 4px; font-size: 11px;")
        self.get_ext_btn.clicked.connect(self.on_open_extension_url)
        ext_row.addWidget(self.get_ext_btn)
        pt_layout.addLayout(ext_row)

        guide_lbl = QLabel("1. Install 'Get cookies.txt LOCALLY' extension in Brave/Chrome.\n2. Open youtube.com & click extension -> Export/Copy.\n3. Click 'Paste from Clipboard' below & Save:")
        guide_lbl.setStyleSheet("color: #cbd5e1; font-size: 11px; background-color: #1e293b; padding: 8px; border-radius: 4px;")
        pt_layout.addWidget(guide_lbl)

        self.paste_text = QPlainTextEdit()
        self.paste_text.setPlaceholderText("# Paste your Netscape cookies text here...")
        pt_layout.addWidget(self.paste_text)

        p_btn_row = QHBoxLayout()
        self.paste_clip_btn = QPushButton("📋 Paste from Clipboard")
        self.paste_clip_btn.setStyleSheet("background-color: #7928ca; color: #fff; font-weight: bold; padding: 8px 14px; border-radius: 4px;")
        self.paste_clip_btn.clicked.connect(self.on_paste_clipboard)
        p_btn_row.addWidget(self.paste_clip_btn)

        self.save_pasted_btn = QPushButton("💾 Save Cookies to App")
        self.save_pasted_btn.setStyleSheet("background-color: #10b981; color: #000; font-weight: bold; padding: 8px 14px; border-radius: 4px;")
        self.save_pasted_btn.clicked.connect(self.on_save_pasted)
        p_btn_row.addWidget(self.save_pasted_btn)
        pt_layout.addLayout(p_btn_row)
        self.tabs.addTab(paste_tab, "⭐ Paste Cookies (Recommended)")

        # TAB 2: File Picker
        file_tab = QWidget()
        ft_layout = QVBoxLayout(file_tab)
        ft_layout.setContentsMargins(14, 14, 14, 14)
        ft_layout.setSpacing(12)

        ft_info = QLabel("Import an existing cookies.txt file from your computer:")
        ft_info.setWordWrap(True)
        ft_layout.addWidget(ft_info)

        self.import_file_btn = QPushButton("📁 Select & Import cookies.txt File...")
        self.import_file_btn.setStyleSheet("background-color: #00f0ff; color: #000; font-weight: bold; padding: 10px; border-radius: 6px; font-size: 12px;")
        self.import_file_btn.clicked.connect(self.on_import_file)
        ft_layout.addWidget(self.import_file_btn)
        ft_layout.addStretch()
        self.tabs.addTab(file_tab, "📁 Import File")

        # TAB 3: Extract from Browser
        extract_tab = QWidget()
        et_layout = QVBoxLayout(extract_tab)
        et_layout.setContentsMargins(14, 14, 14, 14)
        et_layout.setSpacing(12)

        info1 = QLabel("Automatically grabs YouTube authentication cookies from your browser profile and saves to cookies.txt:")
        info1.setWordWrap(True)
        et_layout.addWidget(info1)

        b_row = QHBoxLayout()
        b_row.addWidget(QLabel("Select Browser:"))
        self.browser_combo = QComboBox()
        self.browser_combo.addItems(["Brave", "Chrome", "Firefox", "Edge", "Opera", "Vivaldi"])
        self.browser_combo.setStyleSheet("background-color: #1e293b; color: #fff; padding: 6px; border-radius: 4px;")
        b_row.addWidget(self.browser_combo, 1)
        et_layout.addLayout(b_row)

        self.extract_btn = QPushButton("⚡ Extract Cookies from Browser")
        self.extract_btn.setStyleSheet("background-color: #00f0ff; color: #000; font-weight: bold; padding: 8px; border-radius: 6px; font-size: 12px;")
        self.extract_btn.clicked.connect(self.on_extract_browser)
        et_layout.addWidget(self.extract_btn)

        note_lbl = QLabel("💡 Note: Windows blocks external apps from decrypting Chromium 127+ cookies directly on disk. If this fails, use the 'Paste Cookies' tab.")
        note_lbl.setStyleSheet("color: #94a3b8; font-size: 11px; font-style: italic;")
        note_lbl.setWordWrap(True)
        et_layout.addWidget(note_lbl)
        et_layout.addStretch()
        self.tabs.addTab(extract_tab, "⚡ Direct Browser Extract")

        layout.addWidget(self.tabs)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("background-color: #1e293b; color: #fff; padding: 8px; border-radius: 6px;")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def update_status(self):
        from downloader import get_cookie_status
        has_cookies, count, msg = get_cookie_status("cookies.txt")
        if has_cookies:
            self.status_icon_lbl.setText("🟢")
            self.status_text_lbl.setText(f"Active: {msg}")
            self.status_text_lbl.setStyleSheet("font-size: 12px; font-weight: bold; color: #10b981;")
            self.status_box.setStyleSheet("background-color: #16192b; border: 1px solid #10b981; border-radius: 8px; padding: 10px;")
            self.clear_cookies_btn.setEnabled(True)
        else:
            self.status_icon_lbl.setText("⚪")
            self.status_text_lbl.setText(msg)
            self.status_text_lbl.setStyleSheet("font-size: 12px; font-weight: bold; color: #94a3b8;")
            self.status_box.setStyleSheet("background-color: #16192b; border: 1px solid #334155; border-radius: 8px; padding: 10px;")
            self.clear_cookies_btn.setEnabled(False)

    def on_extract_browser(self):
        from downloader import extract_browser_cookies
        browser = self.browser_combo.currentText()
        success, msg = extract_browser_cookies(browser, "cookies.txt")
        if success:
            CyberMessageBox.show_info(self, "Cookies Extracted", f"🎉 {msg}\n\nAll downloads will now automatically use your {browser} session!", border_color="#10b981")
        else:
            CyberMessageBox.show_info(self, "Extraction Notice", f"⚠️ {msg}", border_color="#ff007f")
        self.update_status()

    def on_open_extension_url(self):
        import webbrowser
        webbrowser.open("https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc")

    def on_paste_clipboard(self):
        clip = QApplication.clipboard()
        text = clip.text()
        if text:
            self.paste_text.setPlainText(text)
        else:
            CyberMessageBox.show_info(self, "Clipboard Empty", "No text found in clipboard.")

    def on_save_pasted(self):
        text = self.paste_text.toPlainText().strip()
        if not text:
            CyberMessageBox.show_info(self, "Empty Text", "Please paste valid cookie text first.", border_color="#ff007f")
            return
        try:
            with open("cookies.txt", "w", encoding="utf-8") as f:
                f.write(text)
            CyberMessageBox.show_info(self, "Saved", "🎉 Cookies saved successfully to cookies.txt!\n\nAll YouTube downloads will now use this session.", border_color="#10b981")
            self.update_status()
        except Exception as e:
            CyberMessageBox.show_info(self, "Error Saving", f"Failed to save cookies: {str(e)}", border_color="#ff007f")

    def on_import_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select cookies.txt", os.path.expanduser("~"), "Cookie Files (*.txt *.cookies);;All Files (*.*)")
        if file_path:
            try:
                import shutil
                shutil.copy2(file_path, "cookies.txt")
                CyberMessageBox.show_info(self, "Import Successful", f"🎉 Successfully imported {os.path.basename(file_path)} into the application!", border_color="#10b981")
                self.update_status()
            except Exception as e:
                CyberMessageBox.show_info(self, "Import Failed", f"Failed to import file: {str(e)}", border_color="#ff007f")

    def on_clear_cookies(self):
        if os.path.exists("cookies.txt"):
            try:
                os.remove("cookies.txt")
                CyberMessageBox.show_info(self, "Cleared", "Cookies removed. App is now in anonymous mode.", border_color="#00f0ff")
                self.update_status()
            except Exception as e:
                CyberMessageBox.show_info(self, "Error", f"Could not remove cookies: {str(e)}", border_color="#ff007f")


class ProfileTreeWidget(QTreeWidget):
    profile_moved = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)

    def dragEnterEvent(self, event):
        item = self.currentItem()
        if item and item.data(0, Qt.ItemDataRole.UserRole) == "profile":
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        target_item = self.itemAt(event.position().toPoint())
        dragged_item = self.currentItem()
        
        if not dragged_item or dragged_item.data(0, Qt.ItemDataRole.UserRole) != "profile":
            event.ignore()
            return
            
        new_folder = ""
        if target_item:
            role = target_item.data(0, Qt.ItemDataRole.UserRole)
            if role == "folder":
                new_folder = target_item.data(0, Qt.ItemDataRole.UserRole + 1)
            elif role == "profile":
                parent = target_item.parent()
                if parent:
                    new_folder = parent.data(0, Qt.ItemDataRole.UserRole + 1)
        
        profile_name = dragged_item.data(0, Qt.ItemDataRole.UserRole + 1)
        event.setDropAction(Qt.DropAction.IgnoreAction)
        event.accept()
        self.profile_moved.emit(profile_name, new_folder)


class ToolDownloadWorker(QThread):
    progress_updated = pyqtSignal(str, float)
    completed = pyqtSignal(str, bool, str)

    def __init__(self, dep_manager, tool_name, is_update=False):
        super().__init__()
        self.dep_manager = dep_manager
        self.tool_name = tool_name
        self.is_update = is_update

    def run(self):
        try:
            def cb(percent):
                self.progress_updated.emit(self.tool_name, percent)
            if self.is_update:
                self.dep_manager.update_tool(self.tool_name, cb)
            else:
                self.dep_manager.download_tool(self.tool_name, cb)
            self.completed.emit(self.tool_name, True, "")
        except Exception as e:
            self.completed.emit(self.tool_name, False, str(e))


class BatchToolUpdateWorker(QThread):
    overall_progress = pyqtSignal(int, int, str, float)  # current_idx, total, current_tool, percent
    tool_finished = pyqtSignal(str, bool, str)           # tool_name, success, error_msg
    all_finished = pyqtSignal(list)                      # list of (tool_name, success, error_msg)

    def __init__(self, dep_manager, tools_list):
        super().__init__()
        self.dep_manager = dep_manager
        self.tools_list = tools_list

    def run(self):
        results = []
        total = len(self.tools_list)
        for idx, tool in enumerate(self.tools_list):
            def cb(percent):
                self.overall_progress.emit(idx + 1, total, tool, percent)
            self.overall_progress.emit(idx + 1, total, tool, 0.0)
            try:
                self.dep_manager.update_tool(tool, cb)
                results.append((tool, True, ""))
                self.tool_finished.emit(tool, True, "")
            except Exception as e:
                results.append((tool, False, str(e)))
                self.tool_finished.emit(tool, False, str(e))
        self.all_finished.emit(results)

class ToolDiagnosticWorker(QThread):
    finished = pyqtSignal(str, str, str)  # tool_name, status, message

    def __init__(self, dep_manager, tool_name, parent=None):
        super().__init__(parent)
        self.dep_manager = dep_manager
        self.tool_name = tool_name

    def run(self):
        try:
            status, msg = self.dep_manager.quick_test_tool(self.tool_name)
            self.finished.emit(self.tool_name, status, msg)
        except Exception as e:
            self.finished.emit(self.tool_name, "warning", str(e))


class BatchToolDiagnosticWorker(QThread):
    tool_tested = pyqtSignal(str, str, str)  # tool_name, status, message
    all_finished = pyqtSignal(dict)           # {tool_name: (status, message)}

    def __init__(self, dep_manager, tools=None, parent=None):
        super().__init__(parent)
        self.dep_manager = dep_manager
        self.tools = tools or ["yt-dlp", "aria2c", "ffmpeg", "spotdl", "gallery-dl", "instagram"]

    def run(self):
        results = {}
        for t in self.tools:
            try:
                status, msg = self.dep_manager.quick_test_tool(t)
            except Exception as e:
                status, msg = "warning", str(e)
            results[t] = (status, msg)
            self.tool_tested.emit(t, status, msg)
        self.all_finished.emit(results)


class MetadataProbeWorker(QThread):
    metadata_ready = pyqtSignal(str, str, str, bytes)  # download_id, title, uploader, thumb_bytes

    def __init__(self, download_id, url, tool, parent=None):
        super().__init__(parent)
        self.download_id = download_id
        self.url = url
        self.tool = tool

    def run(self):
        title = ""
        uploader = ""
        thumb_bytes = b""
        try:
            u_lower = self.url.lower()
            if "youtube.com" in u_lower or "youtu.be" in u_lower:
                from dependency_manager import BIN_DIR
                yt_path = os.path.join(BIN_DIR, "yt-dlp.exe")
                if os.path.exists(yt_path):
                    flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                    cmd = [yt_path, "--dump-single-json", "--no-playlist", "--skip-download", self.url]
                    res = subprocess.run(cmd, capture_output=True, text=True, timeout=6, creationflags=flags)
                    if res.returncode == 0 and res.stdout:
                        data = json.loads(res.stdout)
                        title = data.get("title", "")
                        uploader = data.get("uploader", "") or data.get("channel", "")
                        thumb_url = data.get("thumbnail", "")
                        if thumb_url:
                            resp = requests.get(thumb_url, timeout=3)
                            if resp.status_code == 200:
                                thumb_bytes = resp.content
            elif "spotify.com" in u_lower:
                try:
                    headers = {"User-Agent": "Mozilla/5.0"}
                    resp = requests.get(self.url, headers=headers, timeout=4)
                    if resp.status_code == 200:
                        import re
                        m_title = re.search(r'<meta property="og:title" content="([^"]+)"', resp.text)
                        m_desc = re.search(r'<meta property="og:description" content="([^"]+)"', resp.text)
                        m_img = re.search(r'<meta property="og:image" content="([^"]+)"', resp.text)
                        if m_title:
                            title = m_title.group(1)
                        if m_desc:
                            uploader = m_desc.group(1)
                        if m_img:
                            i_resp = requests.get(m_img.group(1), timeout=3)
                            if i_resp.status_code == 200:
                                thumb_bytes = i_resp.content
                except Exception:
                    pass
        except Exception:
            pass

        if title or thumb_bytes:
            self.metadata_ready.emit(self.download_id, title, uploader, thumb_bytes)


class DownloadProgressWidget(QFrame):
    cancelled = pyqtSignal(str)
    retry_requested = pyqtSignal(str)

    def __init__(self, download_id, url, target_dir="", enable_animations=True, parent=None):
        super().__init__(parent)
        self.download_id = download_id
        self.url = url
        self.target_dir = target_dir
        self.enable_animations = enable_animations
        self.setObjectName("progress_card")
        self.setup_ui()

        # Smooth entrance fade-in animation
        if self.enable_animations:
            self.opacity_effect = QGraphicsOpacityEffect(self)
            self.setGraphicsEffect(self.opacity_effect)
            self.fade_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
            self.fade_anim.setDuration(260)
            self.fade_anim.setStartValue(0.0)
            self.fade_anim.setEndValue(1.0)
            self.fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.fade_anim.start()

        # Smooth progress bar value transition animation
        self.progress_anim = QPropertyAnimation(self.progress_bar, b"value")
        self.progress_anim.setDuration(180)
        self.progress_anim.setEasingCurve(QEasingCurve.Type.OutQuad)

    def setup_ui(self):
        card_main_layout = QHBoxLayout(self)
        card_main_layout.setContentsMargins(12, 10, 12, 10)
        card_main_layout.setSpacing(12)

        # Optional Thumbnail Preview on the left
        self.thumb_lbl = QLabel()
        self.thumb_lbl.setFixedSize(52, 52)
        self.thumb_lbl.setStyleSheet("background-color: #060810; border: 1px solid #1a1e32; border-radius: 6px;")
        self.thumb_lbl.setScaledContents(True)
        self.thumb_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumb_lbl.setVisible(False)
        card_main_layout.addWidget(self.thumb_lbl)

        # Right-side details container
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(7)
        card_main_layout.addLayout(layout, 1)

        # Service Icon detection
        u_lower = self.url.lower()
        if "spotify.com" in u_lower:
            svc_prefix = "🎵 SPOTIFY"
            svc_color = "#1db954"
        elif "youtube.com" in u_lower or "youtu.be" in u_lower:
            svc_prefix = "🎬 YOUTUBE"
            svc_color = "#ff0000"
        elif "instagram.com" in u_lower:
            svc_prefix = "📸 INSTAGRAM"
            svc_color = "#e1306c"
        elif any(ext in u_lower for ext in [".png", ".jpg", ".jpeg", ".gif", ".webp"]):
            svc_prefix = "🖼️ GALLERY"
            svc_color = "#a855f7"
        else:
            svc_prefix = "📦 DIRECT"
            svc_color = "#00f0ff"

        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        self.svc_tag = QLabel(svc_prefix)
        self.svc_tag.setStyleSheet(f"font-size: 10px; font-weight: 900; color: {svc_color}; background: rgba(0,0,0,0.5); border: 1px solid {svc_color}; border-radius: 4px; padding: 2px 6px; letter-spacing: 1px;")
        top_row.addWidget(self.svc_tag)

        display_url = self.url
        if len(display_url) > 70:
            display_url = display_url[:67] + "..."
        
        self.url_label = QLabel(display_url)
        self.url_label.setStyleSheet("font-weight: 700; color: #ffffff; font-size: 13px;")
        self.url_label.setToolTip(self.url)
        top_row.addWidget(self.url_label, 1)

        self.open_dir_btn = QPushButton("📂 Open Folder")
        self.open_dir_btn.setObjectName("neon_cyan_btn")
        self.open_dir_btn.setFixedHeight(26)
        self.open_dir_btn.setVisible(False)
        self.open_dir_btn.clicked.connect(self.on_open_folder_clicked)

        self.retry_btn = QPushButton("🔄 Retry")
        self.retry_btn.setObjectName("neon_cyan_btn")
        self.retry_btn.setFixedWidth(75)
        self.retry_btn.setFixedHeight(26)
        self.retry_btn.setVisible(False)
        self.retry_btn.clicked.connect(self.on_retry_clicked)

        self.action_btn = QPushButton("Cancel")
        self.action_btn.setObjectName("neon_magenta_btn")
        self.action_btn.setFixedWidth(75)
        self.action_btn.setFixedHeight(26)
        self.action_btn.clicked.connect(self.on_action_clicked)

        top_row.addWidget(self.open_dir_btn)
        top_row.addWidget(self.retry_btn)
        top_row.addWidget(self.action_btn)
        layout.addLayout(top_row)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(11)
        layout.addWidget(self.progress_bar)

        # Status row
        status_row = QHBoxLayout()
        status_row.setSpacing(8)

        self.status_label = QLabel("Initializing ingest engine...")
        self.status_label.setStyleSheet("color: #94a3b8; font-size: 12px;")
        
        self.metrics_label = QLabel("")
        self.metrics_label.setStyleSheet("color: #00f0ff; font-weight: 700; font-size: 11px; padding: 2px 8px; border-radius: 6px; background-color: rgba(0, 240, 255, 0.08); border: 1px solid rgba(0, 240, 255, 0.3); font-family: 'JetBrains Mono', Consolas, monospace;")
        self.metrics_label.setVisible(False)

        status_row.addWidget(self.status_label, 1)
        status_row.addWidget(self.metrics_label)
        layout.addLayout(status_row)

    def set_media_metadata(self, title, uploader, thumb_bytes):
        """Displays rich video / audio title and album art cover thumbnail."""
        if title:
            display_title = title if len(title) <= 70 else title[:67] + "..."
            self.url_label.setText(display_title)
            self.url_label.setToolTip(f"{title}\nBy: {uploader}\n{self.url}")
        if uploader:
            base_svc = self.svc_tag.text().split(" • ")[0]
            self.svc_tag.setText(f"{base_svc} • {uploader[:18]}")
        if thumb_bytes:
            pixmap = QPixmap()
            if pixmap.loadFromData(thumb_bytes):
                self.thumb_lbl.setPixmap(pixmap)
                self.thumb_lbl.setVisible(True)

    def set_queued(self):
        self.setProperty("state", "queued")
        self.style().unpolish(self)
        self.style().polish(self)

        self.progress_anim.stop()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Queued")
        self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #f59e0b; }")
        
        self.status_label.setText("⏳ Waiting in queue for available slot...")
        self.status_label.setStyleSheet("color: #f59e0b; font-weight: 700;")
        self.metrics_label.setText("IN QUEUE")
        self.metrics_label.setStyleSheet("color: #f59e0b; font-weight: 700; font-size: 11px; padding: 2px 8px; border-radius: 6px; background-color: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.35); font-family: 'JetBrains Mono', Consolas, monospace;")
        self.metrics_label.setVisible(True)
        
        self.retry_btn.setVisible(False)
        self.action_btn.setText("Cancel")
        self.action_btn.setObjectName("neon_magenta_btn")
        try:
            self.action_btn.clicked.disconnect()
        except Exception:
            pass
        self.action_btn.clicked.connect(self.on_action_clicked)

    def set_running(self):
        self.setProperty("state", "running")
        self.style().unpolish(self)
        self.style().polish(self)

        self.progress_bar.setStyleSheet("")
        self.progress_bar.setFormat("%p%")
        self.status_label.setText("● Connecting and ingesting...")
        self.status_label.setStyleSheet("color: #00f0ff; font-weight: 700; font-size: 12px;")
        self.metrics_label.setText("ACTIVE")
        self.metrics_label.setStyleSheet("color: #00f0ff; font-weight: 700; font-size: 11px; padding: 2px 8px; border-radius: 6px; background-color: rgba(0, 240, 255, 0.08); border: 1px solid rgba(0, 240, 255, 0.35); font-family: 'JetBrains Mono', Consolas, monospace;")
        self.metrics_label.setVisible(True)
        self.retry_btn.setVisible(False)

    def update_progress(self, percent, speed, eta, status):
        if percent >= 0:
            if self.progress_bar.maximum() == 0:
                self.progress_bar.setMaximum(100)
            target_val = int(percent)
            if self.progress_bar.value() != target_val:
                if self.enable_animations:
                    self.progress_anim.stop()
                    self.progress_anim.setStartValue(self.progress_bar.value())
                    self.progress_anim.setEndValue(target_val)
                    self.progress_anim.start()
                else:
                    self.progress_anim.stop()
                    self.progress_bar.setValue(target_val)
            if percent == 100:
                self.progress_bar.setFormat("100% (Completed)")
            else:
                self.progress_bar.setFormat(f"{percent}%")
        else:
            self.progress_anim.stop()
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(0)
            self.progress_bar.setFormat("")
        
        self.status_label.setText(status)
        if (not speed or speed == "-") and (not eta or eta == "-"):
            self.metrics_label.setText("")
            self.metrics_label.setVisible(False)
        else:
            self.metrics_label.setVisible(True)
            self.metrics_label.setText(f"⚡ {speed}  ⏱ {eta}")

    def set_error(self, error_msg):
        self.setProperty("state", "error")
        self.style().unpolish(self)
        self.style().polish(self)

        self.progress_anim.stop()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #ff0055; }")
        self.status_label.setText(f"✖ Error: {error_msg}")
        self.status_label.setStyleSheet("color: #ff0055; font-weight: bold;")
        self.metrics_label.setText("FAILED")
        self.metrics_label.setStyleSheet("color: #ff0055; font-weight: 700; font-size: 11px; padding: 2px 8px; border-radius: 6px; background-color: rgba(255, 0, 85, 0.1); border: 1px solid rgba(255, 0, 85, 0.35); font-family: 'JetBrains Mono', Consolas, monospace;")
        self.metrics_label.setVisible(True)
        
        self.retry_btn.setVisible(True)
        self.action_btn.setText("Clear")
        self.action_btn.setObjectName("neon_magenta_btn")
        try:
            self.action_btn.clicked.disconnect()
        except Exception:
            pass
        self.action_btn.clicked.connect(self.on_remove_clicked)

    def set_completed(self):
        self.setProperty("state", "completed")
        self.style().unpolish(self)
        self.style().polish(self)

        self.progress_anim.stop()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(100)
        self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #00ff88; }")
        self.status_label.setText("✔ Ingest completed successfully")
        self.status_label.setStyleSheet("color: #00ff88; font-weight: 700;")
        self.metrics_label.setText("FINISHED")
        self.metrics_label.setStyleSheet("color: #00ff88; font-weight: 700; font-size: 11px; padding: 2px 8px; border-radius: 6px; background-color: rgba(0, 255, 136, 0.1); border: 1px solid rgba(0, 255, 136, 0.35); font-family: 'JetBrains Mono', Consolas, monospace;")
        self.metrics_label.setVisible(True)
        
        self.retry_btn.setVisible(False)
        if self.target_dir and os.path.exists(self.target_dir):
            self.open_dir_btn.setVisible(True)

        self.action_btn.setText("Clear")
        self.action_btn.setObjectName("neon_cyan_btn")
        try:
            self.action_btn.clicked.disconnect()
        except Exception:
            pass
        self.action_btn.clicked.connect(self.on_remove_clicked)

    def on_action_clicked(self):
        self.cancelled.emit(self.download_id)

    def on_retry_clicked(self):
        self.retry_requested.emit(self.download_id)

    def on_remove_clicked(self):
        self.setParent(None)
        self.deleteLater()

    def on_open_folder_clicked(self):
        if self.target_dir and os.path.exists(self.target_dir):
            os.startfile(self.target_dir)


class CyberProfileBadge(QPushButton):
    """
    Sleek Cyberpunk Profile Pill with neon rounded glow and an animated
    purple-black-white color gradient moving continuously across the text on the X-axis.
    """
    def __init__(self, text="@ssprata", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Developed by @ssprata — Click to view GitHub projects & other tools\nhttps://github.com/ssprata")
        self.setFixedHeight(26)
        self.setMinimumWidth(105)
        self._phase = 0.0
        self._glow_phase = 0.0
        self._glow_dir = 1

        self.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/ssprata")))

        # Smooth horizontal gradient animation timer (~33 FPS)
        self._anim_timer = QTimer(self)
        self._anim_timer.timeout.connect(self._step_gradient)
        self._anim_timer.start(30)

    def _step_gradient(self):
        # Shift gradient wave along X axis
        self._phase = (self._phase + 0.015) % 1.0

        # Gentle breathing neon glow
        self._glow_phase += 0.04 * self._glow_dir
        if self._glow_phase >= 1.0:
            self._glow_phase = 1.0
            self._glow_dir = -1
        elif self._glow_phase <= 0.0:
            self._glow_phase = 0.0
            self._glow_dir = 1
        
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        w = float(self.width())
        h = float(self.height())

        inset = 2.0
        pill_w = w - (inset * 2.0)
        pill_h = h - (inset * 2.0)
        radius = pill_h / 2.0

        # 1. Outer Neon Rounding Glow (Multi-layered diffused halo)
        glow_alpha = int(45 + 35 * self._glow_phase)
        for i in range(3, 0, -1):
            glow_color = QColor(168, 85, 247, int(glow_alpha / (i * 1.4)))
            painter.setPen(QPen(glow_color, float(i * 1.5)))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(QRectF(inset, inset, pill_w, pill_h), radius, radius)

        # 2. Pill Background & Neon Rim
        bg_col = QColor(8, 7, 16, 245)
        border_col = QColor(192, 132, 252, int(200 + 55 * self._glow_phase))
        if self.isDown():
            bg_col = QColor(25, 12, 45, 255)
            border_col = QColor(236, 72, 153, 255)
        elif self.underMouse():
            bg_col = QColor(18, 12, 32, 250)
            border_col = QColor(240, 190, 255, 255)

        painter.setPen(QPen(border_col, 1.3))
        painter.setBrush(QBrush(bg_col))
        painter.drawRoundedRect(QRectF(inset, inset, pill_w, pill_h), radius, radius)

        # 3. Text layout & moving horizontal gradient (Purple -> Black -> White -> Purple)
        font = self.font()
        font.setBold(True)
        font.setPointSize(10)
        font.setFamily("Segoe UI")
        painter.setFont(font)

        fm = painter.fontMetrics()
        txt = self.text()
        tw = float(fm.horizontalAdvance(txt))
        th = float(fm.capHeight())
        tx = (w - tw) / 2.0
        ty = (h + th) / 2.0 - 1.0

        # Moving X-axis linear gradient
        cycle_len = tw + 45.0
        x_start = tx - 25.0 + (self._phase * cycle_len)
        x_end = x_start + cycle_len
        grad = QLinearGradient(x_start, 0.0, x_end, 0.0)
        grad.setSpread(QLinearGradient.Spread.RepeatSpread)

        # Purple -> Black -> White -> Purple color stops
        grad.setColorAt(0.00, QColor("#c084fc")) # Light Vibrant Purple
        grad.setColorAt(0.25, QColor("#7928ca")) # Deep Violet-Purple
        grad.setColorAt(0.48, QColor("#080511")) # OLED Black / Deep Obsidian
        grad.setColorAt(0.72, QColor("#ffffff")) # Glowing White
        grad.setColorAt(0.85, QColor("#e9d5ff")) # Pale Lavender White
        grad.setColorAt(1.00, QColor("#c084fc")) # Light Vibrant Purple

        path = QPainterPath()
        path.addText(tx, ty, font, txt)
        painter.fillPath(path, QBrush(grad))

        # Delicate neon rim on text so black gradient phase remains ultra-crisp
        painter.strokePath(path, QPen(QColor(192, 132, 252, 110), 0.6))
        painter.end()



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nexus — High-Speed Media Ingest")
        self.resize(1180, 820)
        self.setMinimumSize(980, 680)

        # Managers
        self.config_manager = ConfigManager()
        self.dep_manager = DependencyManager()
        self.history_manager = HistoryManager()

        # Trackers & Concurrency Queue
        self.active_workers = {}   # download_id -> (worker, progress_card, job_info)
        self.pending_queue = []    # list of job_info dicts
        self.active_speeds = {}    # download_id -> speed_str
        self.job_registry = {}     # download_id -> job_info
        self.max_concurrent_downloads = self.config_manager.get_max_concurrent_downloads()
        self.tool_download_workers = {}
        self.batch_update_worker = None
        self.engine_badges = {}
        self.expanded_folders = set()
        self.is_loading_profile = False
        self.zombie_workers = set()   # Retain QThread references during cancellation until finished signal fires
        self.probe_workers = {}
        self.tool_diagnostic_workers = {}
        self.batch_diagnostic_worker = None
        self.last_sniffed_url = ""
        self.clipboard = QApplication.clipboard()
        self.clipboard.dataChanged.connect(self.on_clipboard_changed)

        # Build UI
        self.setup_ui()
        self.setup_system_tray()
        self.load_profiles()
        self.refresh_tools_status()
        self.load_history_table()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ----------------- TOP HEADER BAR -----------------
        header_bar = QFrame()
        header_bar.setObjectName("top_header_bar")
        header_layout = QHBoxLayout(header_bar)
        header_layout.setContentsMargins(18, 10, 18, 10)
        header_layout.setSpacing(14)

        # Brand / Title
        brand_layout = QVBoxLayout()
        brand_layout.setSpacing(2)
        app_title = QLabel("⚡ NEXUS")
        app_title.setObjectName("app_title")
        app_subtitle = QLabel("HIGH-SPEED MEDIA INGEST")
        app_subtitle.setObjectName("app_subtitle")
        brand_layout.addWidget(app_title)
        brand_layout.addWidget(app_subtitle)
        header_layout.addLayout(brand_layout)

        header_layout.addSpacing(16)

        # Live Engine Badges in Header (Compact clickable logo pills)
        self.engine_badges_layout = QHBoxLayout()
        self.engine_badges_layout.setSpacing(6)
        TOOL_META = [
            ("yt-dlp", "yt-dlp"),
            ("aria2c", "aria2c"),
            ("ffmpeg", "ffmpeg"),
            ("spotdl", "spotdl"),
            ("gallery-dl", "g-dl"),
            ("instagram", "insta")
        ]
        for t, display_name in TOOL_META:
            badge = QPushButton(f"{display_name} ●")
            badge.setObjectName("engine_top_pill")
            badge.setProperty("status", "working")
            badge.setToolTip(f"{t}: Checking status...\nClick to inspect in Engine Center")
            badge.setCursor(Qt.CursorShape.PointingHandCursor)
            badge.clicked.connect(lambda checked, tool=t: self.navigate_to_engine(tool))
            self.engine_badges_layout.addWidget(badge)
            self.engine_badges[t] = badge
        header_layout.addLayout(self.engine_badges_layout)

        header_layout.addStretch()

        # Aggregate Speed / Ingest Pulse Indicator
        self.aggregate_speed_lbl = QLabel("● Idle")
        self.aggregate_speed_lbl.setStyleSheet("color: #00f0ff; font-weight: bold; font-size: 12px; padding: 4px 10px; border: 1px solid #1e2030; border-radius: 6px; background-color: #141726;")
        header_layout.addWidget(self.aggregate_speed_lbl)

        # Cookie Manager in Header
        self.cookie_manager_btn = QPushButton("Cookie Manager")
        self.cookie_manager_btn.setObjectName("neon_yellow_btn")
        self.cookie_manager_btn.clicked.connect(self.on_open_cookie_manager)
        header_layout.addWidget(self.cookie_manager_btn)

        # Developer GitHub link in Header (Animated Cyber Profile Badge)
        self.github_profile_btn = CyberProfileBadge("@ssprata")
        header_layout.addWidget(self.github_profile_btn)

        root_layout.addWidget(header_bar)

        # ----------------- MAIN WORKSPACE SPLITTER -----------------
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        root_layout.addWidget(main_splitter, 1)

        # ----------------- LEFT SIDEBAR -----------------
        sidebar = QFrame()
        sidebar.setObjectName("sidebar_frame")
        sidebar.setMinimumWidth(280)
        sidebar.setMaximumWidth(360)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(14, 14, 14, 14)
        sidebar_layout.setSpacing(10)

        # Profile Section Header
        prof_header_layout = QHBoxLayout()
        prof_title = QLabel("📁 PROFILES & DESTINATIONS")
        prof_title.setObjectName("section_title")
        prof_header_layout.addWidget(prof_title)
        prof_header_layout.addStretch()
        sidebar_layout.addLayout(prof_header_layout)

        # Main Ingest Library Root Frame
        self.lib_root_card = QFrame()
        self.lib_root_card.setObjectName("card_frame")
        lib_root_layout = QVBoxLayout(self.lib_root_card)
        lib_root_layout.setContentsMargins(10, 8, 10, 8)
        lib_root_layout.setSpacing(6)

        lib_header_row = QHBoxLayout()
        lib_title = QLabel("🏠 ROOT LIBRARY")
        lib_title.setStyleSheet("font-size: 11px; font-weight: 800; color: #00f0ff; letter-spacing: 0.5px;")
        lib_header_row.addWidget(lib_title)
        lib_header_row.addStretch()

        self.lib_change_btn = QPushButton("Change")
        self.lib_change_btn.setFixedHeight(22)
        self.lib_change_btn.setStyleSheet("font-size: 11px; padding: 2px 8px; background-color: #161b2e; border: 1px solid #00f0ff; color: #00f0ff; border-radius: 4px;")
        self.lib_change_btn.clicked.connect(self.on_change_main_library_dir)
        lib_header_row.addWidget(self.lib_change_btn)

        self.lib_open_btn = QPushButton("Open ↗")
        self.lib_open_btn.setFixedHeight(22)
        self.lib_open_btn.setStyleSheet("font-size: 11px; padding: 2px 8px; background-color: #161b2e; border: 1px solid #7928ca; color: #d8b4fe; border-radius: 4px;")
        self.lib_open_btn.clicked.connect(self.on_open_main_library_dir)
        lib_header_row.addWidget(self.lib_open_btn)

        lib_root_layout.addLayout(lib_header_row)

        self.main_library_lbl = QLabel()
        self.main_library_lbl.setStyleSheet("color: #94a3b8; font-size: 11px; font-family: monospace;")
        self.main_library_lbl.setWordWrap(True)
        lib_root_layout.addWidget(self.main_library_lbl)
        self.update_main_library_label()

        sidebar_layout.addWidget(self.lib_root_card)

        # Profiles Tree List
        self.profiles_list = ProfileTreeWidget()
        self.profiles_list.setHeaderHidden(True)
        self.profiles_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.profiles_list.customContextMenuRequested.connect(self.on_profile_tree_context_menu)
        self.profiles_list.itemClicked.connect(self.on_profile_item_clicked)
        self.profiles_list.profile_moved.connect(self.on_profile_moved)
        self.profiles_list.itemExpanded.connect(self.on_folder_expanded)
        self.profiles_list.itemCollapsed.connect(self.on_folder_collapsed)
        sidebar_layout.addWidget(self.profiles_list, 1)

        # Profile Buttons Row 1: Add Profile, Add Folder, Delete
        prof_btn_row = QHBoxLayout()
        prof_btn_row.setSpacing(6)
        
        self.add_profile_btn = QPushButton("+ Profile")
        self.add_profile_btn.setObjectName("neon_cyan_btn")
        self.add_profile_btn.clicked.connect(self.on_add_profile)
        
        self.add_folder_btn = QPushButton("+ Folder")
        self.add_folder_btn.setObjectName("neon_purple_btn")
        self.add_folder_btn.clicked.connect(self.on_add_folder)
        
        self.delete_profile_btn = QPushButton("- Delete")
        self.delete_profile_btn.setObjectName("neon_magenta_btn")
        self.delete_profile_btn.clicked.connect(self.on_delete_profile)
        
        prof_btn_row.addWidget(self.add_profile_btn)
        prof_btn_row.addWidget(self.add_folder_btn)
        prof_btn_row.addWidget(self.delete_profile_btn)
        sidebar_layout.addLayout(prof_btn_row)

        # Profile Buttons Row 2: Portable Backup & Sharing
        portability_btn_row = QHBoxLayout()
        portability_btn_row.setSpacing(6)

        self.export_profiles_btn = QPushButton("📤 Export")
        self.export_profiles_btn.setObjectName("neon_purple_btn")
        self.export_profiles_btn.setToolTip("Export profiles or folder to portable .nexus bundle")
        self.export_profiles_btn.clicked.connect(lambda: self.on_export_profiles_action())

        self.import_profiles_btn = QPushButton("📥 Import")
        self.import_profiles_btn.setObjectName("neon_yellow_btn")
        self.import_profiles_btn.setToolTip("Import profiles from a .nexus or .json package")
        self.import_profiles_btn.clicked.connect(self.on_import_profiles_action)

        portability_btn_row.addWidget(self.export_profiles_btn)
        portability_btn_row.addWidget(self.import_profiles_btn)
        sidebar_layout.addLayout(portability_btn_row)

        # Active Profile Snapshot Card (Compact Cyberpunk HUD)
        self.active_snapshot_card = QFrame()
        self.active_snapshot_card.setObjectName("snapshot_card")
        snapshot_layout = QVBoxLayout(self.active_snapshot_card)
        snapshot_layout.setContentsMargins(12, 10, 12, 10)
        snapshot_layout.setSpacing(6)

        snap_top_row = QHBoxLayout()
        snap_title = QLabel("⚡ ARMED PROFILE")
        snap_title.setStyleSheet("font-size: 10px; font-weight: 800; color: #ff007f; letter-spacing: 1px;")
        snap_top_row.addWidget(snap_title)
        snap_top_row.addStretch()

        self.snapshot_tool_badge = QLabel("yt-dlp")
        self.snapshot_tool_badge.setObjectName("hud_metric_pill")
        self.snapshot_tool_badge.setStyleSheet("font-size: 10px; padding: 2px 7px; border-radius: 4px; font-weight: 800; background-color: rgba(0, 240, 255, 0.12); color: #00f0ff; border: 1px solid rgba(0, 240, 255, 0.4);")
        snap_top_row.addWidget(self.snapshot_tool_badge)
        snapshot_layout.addLayout(snap_top_row)

        self.snapshot_name_lbl = QLabel("Default Profile")
        self.snapshot_name_lbl.setStyleSheet("font-size: 13px; font-weight: 800; color: #ffffff;")
        snapshot_layout.addWidget(self.snapshot_name_lbl)

        self.snapshot_path_lbl = QLabel()
        self.snapshot_path_lbl.setStyleSheet("font-size: 10px; color: #94a3b8; font-family: 'JetBrains Mono', Consolas, monospace;")
        self.snapshot_path_lbl.setWordWrap(True)
        snapshot_layout.addWidget(self.snapshot_path_lbl)

        snap_btn_row = QHBoxLayout()
        snap_btn_row.setSpacing(6)
        self.snapshot_open_btn = QPushButton("↗ Folder")
        self.snapshot_open_btn.setFixedHeight(24)
        self.snapshot_open_btn.setStyleSheet("font-size: 11px; padding: 2px 8px; background-color: #121524; border: 1px solid #7928ca; color: #d8b4fe; border-radius: 4px;")
        self.snapshot_open_btn.setToolTip("Open this profile's destination directory in File Explorer")
        self.snapshot_open_btn.clicked.connect(self.on_open_current_export_dir)
        snap_btn_row.addWidget(self.snapshot_open_btn)

        self.snapshot_studio_btn = QPushButton("⚙️ Studio ➔")
        self.snapshot_studio_btn.setFixedHeight(24)
        self.snapshot_studio_btn.setStyleSheet("font-size: 11px; padding: 2px 8px; background-color: #121524; border: 1px solid #00f0ff; color: #00f0ff; border-radius: 4px;")
        self.snapshot_studio_btn.setToolTip("Open Profile Studio to customize profile name, engine, and download formats")
        self.snapshot_studio_btn.clicked.connect(lambda: self.main_hub_tabs.setCurrentIndex(1))
        snap_btn_row.addWidget(self.snapshot_studio_btn)

        snapshot_layout.addLayout(snap_btn_row)
        sidebar_layout.addWidget(self.active_snapshot_card)
        main_splitter.addWidget(sidebar)

        # ----------------- RIGHT WORKSPACE AREA -----------------
        workspace = QWidget()
        workspace_layout = QVBoxLayout(workspace)
        workspace_layout.setContentsMargins(12, 12, 12, 12)
        workspace_layout.setSpacing(10)

        # --- Clipboard Ingest Banner (Hidden until media link detected) ---
        self.clipboard_banner = QFrame()
        self.clipboard_banner.setObjectName("clipboard_banner")
        self.clipboard_banner.setVisible(False)
        cb_banner_l = QHBoxLayout(self.clipboard_banner)
        cb_banner_l.setContentsMargins(12, 6, 12, 6)
        cb_banner_l.setSpacing(10)

        self.cb_msg_lbl = QLabel("📋 Media link detected on clipboard")
        self.cb_msg_lbl.setStyleSheet("color: #00f0ff; font-weight: 700; font-size: 12px;")
        cb_banner_l.addWidget(self.cb_msg_lbl, 1)

        self.cb_ingest_btn = QPushButton("⚡ Ingest Now")
        self.cb_ingest_btn.setObjectName("neon_cyan_btn")
        self.cb_ingest_btn.setFixedHeight(26)
        self.cb_ingest_btn.clicked.connect(self.on_clipboard_ingest)
        cb_banner_l.addWidget(self.cb_ingest_btn)

        self.cb_dismiss_btn = QPushButton("✕")
        self.cb_dismiss_btn.setFixedHeight(26)
        self.cb_dismiss_btn.setFixedWidth(28)
        self.cb_dismiss_btn.clicked.connect(lambda: self.clipboard_banner.setVisible(False))
        cb_banner_l.addWidget(self.cb_dismiss_btn)

        workspace_layout.addWidget(self.clipboard_banner)

        # --- Primary Hub Tabs ---
        self.main_hub_tabs = QTabWidget()
        self.main_hub_tabs.setObjectName("activity_tab_widget")
        self.main_hub_tabs.currentChanged.connect(self.on_tab_changed_animate)

        # =========================================================
        # TAB 0: ⚡ Ingest & Queue (Unified Command Center)
        # =========================================================
        ingest_queue_tab = QWidget()
        ingest_queue_layout = QVBoxLayout(ingest_queue_tab)
        ingest_queue_layout.setContentsMargins(10, 10, 10, 10)
        ingest_queue_layout.setSpacing(10)

        # 1. Armed Profile Status Banner
        self.armed_banner = QFrame()
        self.armed_banner.setObjectName("armed_banner")
        armed_banner_layout = QHBoxLayout(self.armed_banner)
        armed_banner_layout.setContentsMargins(14, 8, 14, 8)
        armed_banner_layout.setSpacing(10)

        self.armed_profile_lbl = QLabel("🎯 ARMED PROFILE: Initializing...")
        self.armed_profile_lbl.setStyleSheet("color: #00f0ff; font-size: 12px;")
        armed_banner_layout.addWidget(self.armed_profile_lbl, 1)

        self.armed_studio_btn = QPushButton("⚙️ Configure Profile")
        self.armed_studio_btn.setFixedHeight(26)
        self.armed_studio_btn.setStyleSheet("font-size: 11px; padding: 2px 12px; background-color: #141728; border: 1px solid #00f0ff; color: #00f0ff; border-radius: 5px; font-weight: bold;")
        self.armed_studio_btn.clicked.connect(lambda: self.main_hub_tabs.setCurrentIndex(1))
        armed_banner_layout.addWidget(self.armed_studio_btn)

        ingest_queue_layout.addWidget(self.armed_banner)

        # 2. Batch URL Input Card
        input_card = QFrame()
        input_card.setObjectName("card_frame")
        input_card_layout = QVBoxLayout(input_card)
        input_card_layout.setContentsMargins(14, 12, 14, 12)
        input_card_layout.setSpacing(8)

        url_header_row = QHBoxLayout()
        url_lbl = QLabel("📥 BATCH URL INPUT")
        url_lbl.setObjectName("header_label")
        url_header_row.addWidget(url_lbl)
        url_header_row.addStretch()

        paste_btn = QPushButton("📋 Paste Clipboard")
        paste_btn.setFixedHeight(26)
        paste_btn.clicked.connect(self.on_paste_clipboard)
        url_header_row.addWidget(paste_btn)

        clear_urls_btn = QPushButton("🧹 Clear")
        clear_urls_btn.setFixedHeight(26)
        clear_urls_btn.clicked.connect(self.urls_input_clear)
        url_header_row.addWidget(clear_urls_btn)

        input_card_layout.addLayout(url_header_row)

        self.urls_input = QPlainTextEdit()
        self.urls_input.setPlaceholderText("Paste one or more URLs here (YouTube, Spotify, Direct files, Instagram, Galleries)...")
        self.urls_input.setMinimumHeight(65)
        self.urls_input.setMaximumHeight(105)
        input_card_layout.addWidget(self.urls_input)

        self.download_btn = QPushButton("⚡ ENGAGE DOWNLOAD BATCH")
        self.download_btn.setObjectName("download_btn")
        self.download_btn.clicked.connect(self.start_download_batch)
        input_card_layout.addWidget(self.download_btn)

        ingest_queue_layout.addWidget(input_card)

        # 3. Active Queue Stream & Controls
        queue_card = QFrame()
        queue_card.setObjectName("card_frame")
        queue_card_layout = QVBoxLayout(queue_card)
        queue_card_layout.setContentsMargins(12, 10, 12, 10)
        queue_card_layout.setSpacing(8)

        queue_control_row = QHBoxLayout()
        self.queue_count_lbl = QLabel("Queue: 0 active | 0 queued")
        self.queue_count_lbl.setStyleSheet("color: #00f0ff; font-weight: bold;")
        queue_control_row.addWidget(self.queue_count_lbl)

        queue_control_row.addSpacing(16)
        conc_lbl = QLabel("Max Concurrent:")
        conc_lbl.setStyleSheet("color: #94a3b8; font-size: 12px;")
        queue_control_row.addWidget(conc_lbl)

        self.concurrency_spin = QSpinBox()
        self.concurrency_spin.setRange(1, 6)
        self.concurrency_spin.setValue(self.max_concurrent_downloads)
        self.concurrency_spin.setToolTip("Maximum simultaneous downloads running concurrently (remaining wait in queue)")
        self.concurrency_spin.valueChanged.connect(self.on_concurrency_changed)
        queue_control_row.addWidget(self.concurrency_spin)

        queue_control_row.addStretch()

        self.clear_completed_btn = QPushButton("🧹 Clear Completed")
        self.clear_completed_btn.clicked.connect(self.clear_completed_downloads)
        queue_control_row.addWidget(self.clear_completed_btn)

        self.cancel_all_btn = QPushButton("🛑 Cancel All")
        self.cancel_all_btn.setObjectName("neon_magenta_btn")
        self.cancel_all_btn.clicked.connect(self.cancel_all_downloads)
        queue_control_row.addWidget(self.cancel_all_btn)

        queue_card_layout.addLayout(queue_control_row)

        self.queue_scroll = QScrollArea()
        self.queue_scroll.setWidgetResizable(True)
        self.queue_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.queue_scroll_content = QWidget()
        self.queue_list_layout = QVBoxLayout(self.queue_scroll_content)
        self.queue_list_layout.setContentsMargins(2, 2, 2, 2)
        self.queue_list_layout.setSpacing(8)
        self.queue_list_layout.addStretch()
        self.queue_scroll.setWidget(self.queue_scroll_content)
        queue_card_layout.addWidget(self.queue_scroll, 1)

        ingest_queue_layout.addWidget(queue_card, 1)
        self.main_hub_tabs.addTab(ingest_queue_tab, "⚡ Ingest & Queue (0)")

        # =========================================================
        # TAB 1: ⚙️ Profile Studio (Profile Identity & Engine Tuning)
        # =========================================================
        profile_studio_tab = QWidget()
        studio_layout = QVBoxLayout(profile_studio_tab)
        studio_layout.setContentsMargins(12, 12, 12, 12)
        studio_layout.setSpacing(12)

        # Top Card: Profile Identity & Target Destination
        prof_id_card = QFrame()
        prof_id_card.setObjectName("card_frame")
        prof_id_layout = QVBoxLayout(prof_id_card)
        prof_id_layout.setContentsMargins(14, 12, 14, 12)
        prof_id_layout.setSpacing(10)

        prof_id_title = QLabel("⚙️ ACTIVE PROFILE IDENTITY & TARGET FOLDER")
        prof_id_title.setObjectName("section_title")
        prof_id_layout.addWidget(prof_id_title)

        prof_grid = QGridLayout()
        prof_grid.setSpacing(10)

        prof_grid.addWidget(QLabel("Profile Name:"), 0, 0)
        self.prof_name_input = QLineEdit()
        self.prof_name_input.setPlaceholderText("Profile Name...")
        self.prof_name_input.textChanged.connect(self.on_profile_form_field_changed)
        prof_grid.addWidget(self.prof_name_input, 0, 1)

        prof_grid.addWidget(QLabel("Folder Group:"), 0, 2)
        self.prof_folder_input = QComboBox()
        self.prof_folder_input.setEditable(True)
        self.prof_folder_input.currentTextChanged.connect(self.on_profile_form_field_changed)
        prof_grid.addWidget(self.prof_folder_input, 0, 3)

        prof_grid.addWidget(QLabel("Ingest Engine:"), 0, 4)
        self.prof_tool_combo = QComboBox()
        self.prof_tool_combo.addItems(["yt-dlp", "aria2c", "gallery-dl", "spotdl", "instagram"])
        self.prof_tool_combo.currentTextChanged.connect(self.on_tool_combo_changed)
        prof_grid.addWidget(self.prof_tool_combo, 0, 5)

        self.prof_auto_path_cb = QCheckBox("Auto-mirror folder hierarchy on disk (<Library>/<Folder>/<Profile>)")
        self.prof_auto_path_cb.setStyleSheet("color: #00f0ff; font-weight: bold; font-size: 11px;")
        self.prof_auto_path_cb.toggled.connect(self.on_auto_path_toggled)
        prof_grid.addWidget(self.prof_auto_path_cb, 1, 0, 1, 6)

        prof_grid.addWidget(QLabel("Export Folder:"), 2, 0)
        dir_h_box = QHBoxLayout()
        dir_h_box.setSpacing(8)
        self.prof_dir_input = QLineEdit()
        dir_h_box.addWidget(self.prof_dir_input, 1)

        self.prof_dir_btn = QPushButton("📂 Browse...")
        self.prof_dir_btn.setMinimumWidth(85)
        self.prof_dir_btn.clicked.connect(self.on_browse_directory)
        dir_h_box.addWidget(self.prof_dir_btn)

        self.open_export_dir_btn = QPushButton("↗ Open")
        self.open_export_dir_btn.setMinimumWidth(80)
        self.open_export_dir_btn.clicked.connect(self.on_open_current_export_dir)
        dir_h_box.addWidget(self.open_export_dir_btn)

        prof_grid.addLayout(dir_h_box, 2, 1, 1, 5)

        prof_id_layout.addLayout(prof_grid)

        self.save_profile_btn = QPushButton("💾 Save Profile Settings")
        self.save_profile_btn.setObjectName("neon_cyan_btn")
        self.save_profile_btn.setFixedHeight(30)
        self.save_profile_btn.clicked.connect(self.on_save_profile_settings)
        prof_id_layout.addWidget(self.save_profile_btn)

        studio_layout.addWidget(prof_id_card)

        # Bottom Card: Engine Tuning Tabs for the active profile
        prof_engine_card = QFrame()
        prof_engine_card.setObjectName("card_frame")
        prof_engine_layout = QVBoxLayout(prof_engine_card)
        prof_engine_layout.setContentsMargins(14, 12, 14, 12)
        prof_engine_layout.setSpacing(10)

        prof_engine_title = QLabel("🛠️ ENGINE-SPECIFIC TUNING & FORMAT OPTIONS")
        prof_engine_title.setObjectName("section_title")
        prof_engine_layout.addWidget(prof_engine_title)

        self.config_tabs = QTabWidget()

        # Sub-tab 1: yt-dlp options
        self.ytdlp_tab = QWidget()
        ytdlp_layout = QGridLayout(self.ytdlp_tab)
        ytdlp_layout.setContentsMargins(14, 12, 14, 12)
        ytdlp_layout.setSpacing(10)

        ytdlp_layout.addWidget(QLabel("Video Quality:"), 0, 0)
        self.ytdlp_fmt_combo = QComboBox()
        self.ytdlp_fmt_combo.addItems([
            "bestvideo+bestaudio/best (Best Quality / 4K+)",
            "bestvideo[height<=2160]+bestaudio/best (4K UHD 2160p)",
            "bestvideo[height<=1440]+bestaudio/best (2K QHD 1440p)",
            "bestvideo[height<=1080]+bestaudio/best (FHD 1080p)",
            "bestvideo[height<=720]+bestaudio/best (HD 720p)",
            "bestaudio/best (Audio Only)"
        ])
        ytdlp_layout.addWidget(self.ytdlp_fmt_combo, 0, 1, 1, 3)

        self.ytdlp_audio_cb = QCheckBox("Extract Audio Only")
        self.ytdlp_audio_cb.toggled.connect(self.on_ytdlp_audio_toggled)
        ytdlp_layout.addWidget(self.ytdlp_audio_cb, 1, 0, 1, 2)

        self.ytdlp_video_lbl = QLabel("Video Container:")
        ytdlp_layout.addWidget(self.ytdlp_video_lbl, 1, 2)
        self.ytdlp_video_fmt = QComboBox()
        self.ytdlp_video_fmt.addItems(["best", "mp4", "mkv", "webm"])
        ytdlp_layout.addWidget(self.ytdlp_video_fmt, 1, 3)

        ytdlp_layout.addWidget(QLabel("Audio Format:"), 2, 0)
        self.ytdlp_audio_fmt = QComboBox()
        self.ytdlp_audio_fmt.addItems(["mp3", "m4a", "flac", "opus", "wav"])
        self.ytdlp_audio_fmt.setEnabled(False)
        ytdlp_layout.addWidget(self.ytdlp_audio_fmt, 2, 1)

        ytdlp_layout.addWidget(QLabel("Audio Quality (0 best - 9):"), 2, 2)
        self.ytdlp_audio_q = QSpinBox()
        self.ytdlp_audio_q.setRange(0, 9)
        self.ytdlp_audio_q.setValue(5)
        self.ytdlp_audio_q.setEnabled(False)
        ytdlp_layout.addWidget(self.ytdlp_audio_q, 2, 3)

        self.ytdlp_subs_cb = QCheckBox("Embed Subtitles (when available)")
        self.ytdlp_subs_cb.setChecked(True)
        ytdlp_layout.addWidget(self.ytdlp_subs_cb, 3, 0, 1, 2)

        self.ytdlp_premiere_cb = QCheckBox("🎬 Premiere Pro Ready (H.264/AAC)")
        self.ytdlp_premiere_cb.setToolTip("Automatically ensures video (H.264) and audio (AAC) are 100% compatible with Adobe Premiere Pro and DaVinci Resolve")
        self.ytdlp_premiere_cb.setChecked(True)
        ytdlp_layout.addWidget(self.ytdlp_premiere_cb, 3, 2, 1, 2)

        # Cookie / Authentication source
        ytdlp_layout.addWidget(QLabel("🍪 Cookie / Bot Bypass:"), 4, 0)
        self.ytdlp_cookie_combo = QComboBox()
        self.ytdlp_cookie_combo.addItems([
            "None (Anonymous)",
            "Brave",
            "Chrome",
            "Firefox",
            "Edge",
            "Opera",
            "Vivaldi",
            "Custom cookies.txt File"
        ])
        ytdlp_layout.addWidget(self.ytdlp_cookie_combo, 4, 1)

        cookie_btn_layout = QHBoxLayout()
        self.ytdlp_cookie_btn = QPushButton("📁 Browse...")
        self.ytdlp_cookie_btn.clicked.connect(self.on_browse_cookie_file)
        cookie_btn_layout.addWidget(self.ytdlp_cookie_btn)

        self.ytdlp_open_cookie_mgr_btn = QPushButton("⚡ Cookie Manager")
        self.ytdlp_open_cookie_mgr_btn.setStyleSheet("background-color: #7928ca; color: #fff; font-weight: bold; padding: 4px 8px; border-radius: 4px;")
        self.ytdlp_open_cookie_mgr_btn.clicked.connect(self.on_open_cookie_manager)
        cookie_btn_layout.addWidget(self.ytdlp_open_cookie_mgr_btn)
        ytdlp_layout.addLayout(cookie_btn_layout, 4, 2)

        self.ytdlp_cookie_input = QLineEdit()
        self.ytdlp_cookie_input.setPlaceholderText("Optional path to exported cookies.txt file")
        ytdlp_layout.addWidget(self.ytdlp_cookie_input, 4, 3)

        # Proxy & Sleep requests
        ytdlp_layout.addWidget(QLabel("🌐 Network Proxy:"), 5, 0)
        self.ytdlp_proxy_input = QLineEdit()
        self.ytdlp_proxy_input.setPlaceholderText("socks5://127.0.0.1:1080 or http://user:pass@host:port")
        ytdlp_layout.addWidget(self.ytdlp_proxy_input, 5, 1)

        ytdlp_layout.addWidget(QLabel("⏱ Rate Delay (sec):"), 5, 2)
        self.ytdlp_sleep_input = QLineEdit()
        self.ytdlp_sleep_input.setPlaceholderText("e.g. 1.5 (anti-ban delay between downloads)")
        ytdlp_layout.addWidget(self.ytdlp_sleep_input, 5, 3)

        ytdlp_layout.addWidget(QLabel("Custom Flags:"), 6, 0)
        self.ytdlp_flags_input = QLineEdit()
        self.ytdlp_flags_input.setPlaceholderText("--write-thumbnail --playlist-items 1-5")
        ytdlp_layout.addWidget(self.ytdlp_flags_input, 6, 1, 1, 3)
        self.config_tabs.addTab(self.ytdlp_tab, "⚡ yt-dlp Settings")

        # Sub-tab 2: aria2c options
        self.aria_tab = QWidget()
        aria_layout = QGridLayout(self.aria_tab)
        aria_layout.setContentsMargins(14, 12, 14, 12)
        aria_layout.setSpacing(10)

        aria_layout.addWidget(QLabel("Max Connections:"), 0, 0)
        self.aria_conn_spin = QSpinBox()
        self.aria_conn_spin.setRange(1, 16)
        self.aria_conn_spin.setValue(16)
        aria_layout.addWidget(self.aria_conn_spin, 0, 1)

        aria_layout.addWidget(QLabel("Split Parts:"), 0, 2)
        self.aria_split_spin = QSpinBox()
        self.aria_split_spin.setRange(1, 16)
        self.aria_split_spin.setValue(16)
        aria_layout.addWidget(self.aria_split_spin, 0, 3)

        aria_layout.addWidget(QLabel("Speed Limit (e.g. 5M, 500K, 0=unlimited):"), 1, 0)
        self.aria_speed_input = QLineEdit("0")
        aria_layout.addWidget(self.aria_speed_input, 1, 1, 1, 3)

        aria_layout.addWidget(QLabel("Custom Flags:"), 2, 0)
        self.aria_flags_input = QLineEdit()
        self.aria_flags_input.setPlaceholderText("--header=\"Authorization: Bearer X\"")
        aria_layout.addWidget(self.aria_flags_input, 2, 1, 1, 3)
        self.config_tabs.addTab(self.aria_tab, "🌐 aria2c Settings")

        # Sub-tab 3: spotDL options
        self.spotdl_tab = QWidget()
        spotdl_layout = QGridLayout(self.spotdl_tab)
        spotdl_layout.setContentsMargins(14, 12, 14, 12)
        spotdl_layout.setSpacing(10)

        spotdl_layout.addWidget(QLabel("Audio Format:"), 0, 0)
        self.spotdl_audio_fmt = QComboBox()
        self.spotdl_audio_fmt.addItems(["mp3", "m4a", "flac", "opus", "ogg", "wav"])
        spotdl_layout.addWidget(self.spotdl_audio_fmt, 0, 1)

        spotdl_layout.addWidget(QLabel("Bitrate / Audio Quality:"), 0, 2)
        self.spotdl_audio_q = QComboBox()
        self.spotdl_audio_q.addItems(["auto", "320k", "256k", "192k", "160k", "128k", "disable"])
        spotdl_layout.addWidget(self.spotdl_audio_q, 0, 3)

        spotdl_layout.addWidget(QLabel("Custom Flags:"), 1, 0)
        self.spotdl_flags_input = QLineEdit()
        self.spotdl_flags_input.setPlaceholderText("--user-auth --cookie-file cookies.txt")
        spotdl_layout.addWidget(self.spotdl_flags_input, 1, 1, 1, 3)
        self.config_tabs.addTab(self.spotdl_tab, "🎵 spotDL Settings")

        # Sub-tab 4: Instagram options
        self.instagram_tab = QWidget()
        instagram_layout = QGridLayout(self.instagram_tab)
        instagram_layout.setContentsMargins(14, 12, 14, 12)
        instagram_layout.setSpacing(10)

        self.instagram_pics_cb = QCheckBox("Download Pictures")
        self.instagram_pics_cb.setChecked(True)
        instagram_layout.addWidget(self.instagram_pics_cb, 0, 0)

        self.instagram_vids_cb = QCheckBox("Download Videos (Reels/Posts)")
        self.instagram_vids_cb.setChecked(True)
        instagram_layout.addWidget(self.instagram_vids_cb, 0, 1)

        self.instagram_meta_cb = QCheckBox("Download Metadata & Captions")
        self.instagram_meta_cb.setChecked(False)
        instagram_layout.addWidget(self.instagram_meta_cb, 0, 2)

        self.instagram_comments_cb = QCheckBox("Download Comments")
        self.instagram_comments_cb.setChecked(False)
        instagram_layout.addWidget(self.instagram_comments_cb, 0, 3)

        instagram_layout.addWidget(QLabel("Output Format:"), 1, 0)
        self.instagram_format_combo = QComboBox()
        self.instagram_format_combo.addItems(["Video (mp4)", "Audio Only (m4a)", "Audio Only (mp3)"])
        instagram_layout.addWidget(self.instagram_format_combo, 1, 1, 1, 3)

        instagram_layout.addWidget(QLabel("Custom Flags:"), 2, 0)
        self.instagram_flags_input = QLineEdit()
        self.instagram_flags_input.setPlaceholderText("--login=USERNAME --password=PASSWORD")
        instagram_layout.addWidget(self.instagram_flags_input, 2, 1, 1, 3)
        self.config_tabs.addTab(self.instagram_tab, "📸 Instagram Settings")

        # Sub-tab 5: gallery-dl options
        self.gallerydl_tab = QWidget()
        gallery_layout = QGridLayout(self.gallerydl_tab)
        gallery_layout.setContentsMargins(14, 12, 14, 12)
        gallery_layout.setSpacing(10)

        gallery_layout.addWidget(QLabel("Custom Flags:"), 0, 0)
        self.gallerydl_flags_input = QLineEdit()
        self.gallerydl_flags_input.setPlaceholderText("--range 1-10 --chapters")
        gallery_layout.addWidget(self.gallerydl_flags_input, 0, 1, 1, 3)
        self.config_tabs.addTab(self.gallerydl_tab, "🎨 gallery-dl Settings")

        prof_engine_layout.addWidget(self.config_tabs, 1)
        studio_layout.addWidget(prof_engine_card, 1)
        self.main_hub_tabs.addTab(profile_studio_tab, "⚙️ Profile Studio")

        # =========================================================
        # TAB 2: 🛠️ Engine Center (Diagnostics, Health & Binaries)
        # =========================================================
        engine_center_tab = QWidget()
        engine_center_layout = QVBoxLayout(engine_center_tab)
        engine_center_layout.setContentsMargins(14, 12, 14, 12)
        engine_center_layout.setSpacing(12)

        # Header Control Row
        engines_header_row = QHBoxLayout()
        engines_title = QLabel("ENGINE CENTER & PERFORMANCE")
        engines_title.setStyleSheet("color: #00f0ff; font-weight: 800; font-size: 13px; letter-spacing: 0.8px;")
        engines_header_row.addWidget(engines_title)

        self.engine_health_hud = QLabel("🟢 6/6 Operational")
        self.engine_health_hud.setObjectName("hud_metric_pill")
        engines_header_row.addWidget(self.engine_health_hud)

        engines_header_row.addStretch()

        self.run_all_diag_btn = QPushButton("🧪 Run All Diagnostics")
        self.run_all_diag_btn.setObjectName("neon_cyan_btn")
        self.run_all_diag_btn.clicked.connect(self.run_all_diagnostics)
        engines_header_row.addWidget(self.run_all_diag_btn)

        self.update_all_tab_btn = QPushButton("⚡ Update All Engines")
        self.update_all_tab_btn.setObjectName("neon_purple_btn")
        self.update_all_tab_btn.clicked.connect(self.update_all_engines)
        self.quick_update_btn = self.update_all_tab_btn  # Reference compatibility
        engines_header_row.addWidget(self.update_all_tab_btn)

        engine_center_layout.addLayout(engines_header_row)

        # Download & Diagnostic Progress Bar
        self.tool_progress_lbl = QLabel("")
        self.tool_progress_lbl.setStyleSheet("color: #00f0ff; font-weight: bold;")
        self.tool_progress_bar = QProgressBar()
        self.tool_progress_bar.setVisible(False)
        engine_center_layout.addWidget(self.tool_progress_lbl)
        engine_center_layout.addWidget(self.tool_progress_bar)

        # Interactive Engine Cards Grid (2 rows x 3 columns)
        engines_grid = QGridLayout()
        engines_grid.setSpacing(10)
        self.engine_widgets = {}
        tools_list = [
            ("yt-dlp", "🎬 yt-dlp", "YouTube & Web Video Ingest"),
            ("aria2c", "⚡ aria2c", "Multi-thread Direct Ingest"),
            ("ffmpeg", "🎞️ ffmpeg", "Media Transcoder & Audio Engine"),
            ("spotdl", "🎵 spotdl", "Spotify Music Ingest"),
            ("gallery-dl", "🖼️ gallery-dl", "Image Gallery Ingest"),
            ("instagram", "📸 instagram", "Instagram Media (Instaloader)")
        ]

        for idx, (tool, display_name, desc) in enumerate(tools_list):
            card = QFrame()
            card.setObjectName("engine_card")
            card_l = QVBoxLayout(card)
            card_l.setContentsMargins(12, 10, 12, 10)
            card_l.setSpacing(6)

            c_top = QHBoxLayout()
            t_lbl = QLabel(f"<b>{display_name}</b>")
            t_lbl.setStyleSheet("font-size: 13px; color: #ffffff;")
            c_top.addWidget(t_lbl)
            c_top.addStretch()
            status_badge = QLabel("🟢 Ready")
            status_badge.setObjectName("badge_working")
            c_top.addWidget(status_badge)
            card_l.addLayout(c_top)

            d_lbl = QLabel(desc)
            d_lbl.setStyleSheet("color: #94a3b8; font-size: 11px;")
            card_l.addWidget(d_lbl)

            c_ver = QHBoxLayout()
            c_ver.setSpacing(6)
            v_title = QLabel("Version:")
            v_title.setStyleSheet("color: #64748b; font-size: 11px;")
            c_ver.addWidget(v_title)
            v_lbl = QLabel("Checking...")
            v_lbl.setStyleSheet("color: #00f0ff; font-weight: bold; font-size: 11px; font-family: 'JetBrains Mono', Consolas, monospace;")
            c_ver.addWidget(v_lbl, 1)
            card_l.addLayout(c_ver)

            c_bot = QHBoxLayout()
            c_bot.setSpacing(8)

            test_btn = QPushButton("🧪 Quick Test")
            test_btn.setObjectName("neon_cyan_btn")
            test_btn.setFixedHeight(26)
            test_btn.clicked.connect(lambda checked, t=tool: self.quick_test_engine(t))
            c_bot.addWidget(test_btn, 1)

            update_btn = QPushButton("⚡ Update")
            update_btn.setObjectName("neon_purple_btn")
            update_btn.setFixedHeight(26)
            update_btn.clicked.connect(lambda checked, t=tool: self.download_binary(t, is_update=self.dep_manager.is_installed(t)))
            c_bot.addWidget(update_btn, 1)

            card_l.addLayout(c_bot)

            self.engine_widgets[tool] = {
                "version_lbl": v_lbl,
                "status_badge": status_badge,
                "test_btn": test_btn,
                "btn": update_btn,
                "card": card
            }
            row = idx // 3
            col = idx % 3
            engines_grid.addWidget(card, row, col)

        engine_center_layout.addLayout(engines_grid)
        engine_center_layout.addStretch()
        self.main_hub_tabs.addTab(engine_center_tab, "🛠️ Engine Center")

        # =========================================================
        # TAB 3: 📜 Ingest History
        # =========================================================
        self.history_tab = self.setup_history_tab()
        self.main_hub_tabs.addTab(self.history_tab, "📜 Ingest History")

        # =========================================================
        # TAB 4: 📜 Console Logs
        # =========================================================
        logs_tab = QWidget()
        logs_tab_layout = QVBoxLayout(logs_tab)
        logs_tab_layout.setContentsMargins(10, 10, 10, 10)
        logs_tab_layout.setSpacing(8)

        logs_control_row = QHBoxLayout()
        logs_lbl = QLabel("NEXUS REAL-TIME INGEST STREAM")
        logs_lbl.setStyleSheet("color: #00f0ff; font-weight: bold; font-size: 12px;")
        logs_control_row.addWidget(logs_lbl)

        logs_control_row.addStretch()

        self.autoscroll_cb = QCheckBox("Auto-scroll")
        self.autoscroll_cb.setChecked(True)
        logs_control_row.addWidget(self.autoscroll_cb)

        self.copy_logs_btn = QPushButton("📋 Copy Logs")
        self.copy_logs_btn.clicked.connect(self.copy_logs_to_clipboard)
        logs_control_row.addWidget(self.copy_logs_btn)

        self.clear_logs_btn = QPushButton("🧹 Clear Logs")
        self.clear_logs_btn.clicked.connect(self.clear_logs)
        logs_control_row.addWidget(self.clear_logs_btn)

        logs_tab_layout.addLayout(logs_control_row)

        self.logs_console = QPlainTextEdit()
        self.logs_console.setObjectName("logs_console")
        self.logs_console.setReadOnly(True)
        self.logs_console.setPlaceholderText("Nexus Ingest telemetry and subprocess outputs will stream here...")
        logs_tab_layout.addWidget(self.logs_console)

        self.main_hub_tabs.addTab(logs_tab, "📜 Console Logs")

        # =========================================================
        # TAB 5: ✨ App Tuning & Automation
        # =========================================================
        self.tuning_tab = QWidget()
        tuning_layout = QVBoxLayout(self.tuning_tab)
        tuning_layout.setContentsMargins(14, 12, 14, 12)
        tuning_layout.setSpacing(12)

        # Main Library Ingest Root Frame in Tuning Tab
        lib_tuning_card = QFrame()
        lib_tuning_card.setObjectName("card_frame")
        lib_t_layout = QVBoxLayout(lib_tuning_card)
        lib_t_layout.setContentsMargins(14, 12, 14, 12)
        lib_t_layout.setSpacing(8)

        lib_t_title = QLabel("🏠 MAIN INGEST LIBRARY ROOT")
        lib_t_title.setObjectName("section_title")
        lib_t_layout.addWidget(lib_t_title)

        lib_t_desc = QLabel("Central root directory where auto-managed category and profile sub-folders are created.")
        lib_t_desc.setStyleSheet("color: #94a3b8; font-size: 12px;")
        lib_t_layout.addWidget(lib_t_desc)

        lib_t_row = QHBoxLayout()
        self.tuning_lib_dir_input = QLineEdit()
        self.tuning_lib_dir_input.setReadOnly(True)
        self.tuning_lib_dir_input.setText(self.config_manager.get_main_library_dir())
        self.tuning_lib_browse_btn = QPushButton("📂 Browse...")
        self.tuning_lib_browse_btn.setMinimumWidth(85)
        self.tuning_lib_browse_btn.clicked.connect(self.on_change_main_library_dir)
        lib_t_row.addWidget(self.tuning_lib_dir_input)
        lib_t_row.addWidget(self.tuning_lib_browse_btn)
        lib_t_layout.addLayout(lib_t_row)
        tuning_layout.addWidget(lib_tuning_card)

        tuning_card = QFrame()
        tuning_card.setObjectName("card_frame")
        t_card_layout = QVBoxLayout(tuning_card)
        t_card_layout.setContentsMargins(14, 12, 14, 12)
        t_card_layout.setSpacing(10)

        t_title = QLabel("✨ APPLICATION PREFERENCES & PERFORMANCE")
        t_title.setObjectName("section_title")
        t_card_layout.addWidget(t_title)

        self.enable_animations_cb = QCheckBox("✨ UI Micro-Animations (Smooth progress bar interpolation, card fade-ins, glow transitions)")
        self.enable_animations_cb.setChecked(self.config_manager.get_enable_animations())
        self.enable_animations_cb.toggled.connect(self.on_animations_toggled)
        t_card_layout.addWidget(self.enable_animations_cb)

        self.clipboard_sniffer_cb = QCheckBox("📋 Clipboard Auto-Sniffer (Detect media links on clipboard & offer 1-click ingest banner)")
        self.clipboard_sniffer_cb.setChecked(self.config_manager.get_clipboard_sniffer())
        self.clipboard_sniffer_cb.toggled.connect(self.on_clipboard_sniffer_toggled)
        t_card_layout.addWidget(self.clipboard_sniffer_cb)

        speed_row = QHBoxLayout()
        speed_lbl = QLabel("🌐 Global Bandwidth Limiter:")
        speed_lbl.setStyleSheet("color: #e2e8f0; font-size: 12px;")
        speed_row.addWidget(speed_lbl)
        self.global_speed_combo = QComboBox()
        self.global_speed_combo.addItems([
            "0 (Unlimited / Max Speed)",
            "2M (2 MB/s)",
            "5M (5 MB/s)",
            "10M (10 MB/s)",
            "25M (25 MB/s)"
        ])
        curr_spd = self.config_manager.get_global_speed_limit()
        for i in range(self.global_speed_combo.count()):
            if self.global_speed_combo.itemText(i).startswith(curr_spd):
                self.global_speed_combo.setCurrentIndex(i)
                break
        self.global_speed_combo.currentTextChanged.connect(self.on_global_speed_changed)
        speed_row.addWidget(self.global_speed_combo, 1)
        t_card_layout.addLayout(speed_row)

        tuning_layout.addWidget(tuning_card)

        # Developer & Credits Card
        about_card = QFrame()
        about_card.setObjectName("card_frame")
        about_layout = QVBoxLayout(about_card)
        about_layout.setContentsMargins(14, 12, 14, 12)
        about_layout.setSpacing(10)

        about_title = QLabel("🐙 DEVELOPER & CREDITS")
        about_title.setObjectName("section_title")
        about_layout.addWidget(about_title)

        about_desc = QLabel("Nexus Media Ingest is crafted by <b>@ssprata</b>. Explore other tools, scripts, and open-source projects on GitHub:")
        about_desc.setStyleSheet("color: #94a3b8; font-size: 12px;")
        about_layout.addWidget(about_desc)

        about_btn_row = QHBoxLayout()
        about_btn_row.setSpacing(10)

        dev_gh_btn = QPushButton("Visit @ssprata on GitHub ↗")
        dev_gh_btn.setObjectName("neon_purple_btn")
        dev_gh_btn.setFixedHeight(28)
        dev_gh_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/ssprata")))
        about_btn_row.addWidget(dev_gh_btn)

        repo_gh_btn = QPushButton("Nexus Repository ↗")
        repo_gh_btn.setObjectName("neon_cyan_btn")
        repo_gh_btn.setFixedHeight(28)
        repo_gh_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/ssprata/nexus-media-ingest")))
        about_btn_row.addWidget(repo_gh_btn)

        about_btn_row.addStretch()
        about_layout.addLayout(about_btn_row)
        tuning_layout.addWidget(about_card)

        tuning_layout.addStretch()
        self.main_hub_tabs.addTab(self.tuning_tab, "✨ App Tuning")

        workspace_layout.addWidget(self.main_hub_tabs, 1)
        main_splitter.addWidget(workspace)
        main_splitter.setSizes([320, 880])

        # Connect auto-save signals for tab inputs
        self.connect_auto_save_signals()
        self.update_cookie_header_badge()

    def on_tab_changed_animate(self, index):
        if not self.config_manager.get_enable_animations():
            return
        widget = self.main_hub_tabs.widget(index)
        if widget:
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)
            self._tab_fade_anim = QPropertyAnimation(effect, b"opacity")
            self._tab_fade_anim.setDuration(160)
            self._tab_fade_anim.setStartValue(0.15)
            self._tab_fade_anim.setEndValue(1.0)
            self._tab_fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._tab_fade_anim.start()

    def on_concurrency_changed(self, val):
        self.max_concurrent_downloads = int(val)
        self.config_manager.set_max_concurrent_downloads(val)
        self.process_queue()

    def update_queue_counter(self):
        active_count = len(self.active_workers)
        queued_count = len(self.pending_queue)
        self.queue_count_lbl.setText(f"Queue: {active_count} active | {queued_count} queued")
        self.main_hub_tabs.setTabText(0, f"⚡ Ingest & Queue ({active_count + queued_count})")
        self.update_aggregate_speed()

    def update_aggregate_speed(self):
        active_count = len(self.active_workers)
        queued_count = len(self.pending_queue)
        if active_count == 0 and queued_count == 0:
            self.aggregate_speed_lbl.setText("● Idle")
            self.aggregate_speed_lbl.setStyleSheet("color: #64748b; font-weight: 700; font-size: 12px; padding: 4px 12px; border: 1px solid #141728; border-radius: 7px; background-color: #04050a;")
            return

        speed_list = [s for s in self.active_speeds.values() if s and s != "-"]
        speed_summary = f"● {speed_list[0]}" if speed_list else "● Ingesting"
        self.aggregate_speed_lbl.setText(f"{speed_summary} | {active_count} Active | {queued_count} Queued")
        self.aggregate_speed_lbl.setStyleSheet("color: #00f0ff; font-weight: 800; font-size: 12px; padding: 4px 12px; border: 1px solid #00f0ff; border-radius: 7px; background-color: rgba(0, 240, 255, 0.08); font-family: 'JetBrains Mono', Consolas, monospace;")

    def setup_history_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)

        hist_ctrl_row = QHBoxLayout()
        hist_title = QLabel("DOWNLOAD INGEST ARCHIVE")
        hist_title.setStyleSheet("color: #00f0ff; font-weight: bold; font-size: 12px; letter-spacing: 1px;")
        hist_ctrl_row.addWidget(hist_title)

        hist_ctrl_row.addSpacing(16)

        self.history_search_input = QLineEdit()
        self.history_search_input.setPlaceholderText("🔍 Search history by title, URL or format...")
        self.history_search_input.textChanged.connect(self.filter_history_table)
        hist_ctrl_row.addWidget(self.history_search_input, 1)

        refresh_hist_btn = QPushButton("🔄 Refresh")
        refresh_hist_btn.clicked.connect(self.load_history_table)
        hist_ctrl_row.addWidget(refresh_hist_btn)

        clear_hist_btn = QPushButton("🧹 Clear History")
        clear_hist_btn.setObjectName("neon_magenta_btn")
        clear_hist_btn.clicked.connect(self.on_clear_history)
        hist_ctrl_row.addWidget(clear_hist_btn)

        layout.addLayout(hist_ctrl_row)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels(["Timestamp", "Title / Target", "Engine", "Size", "Status", "Actions"])
        self.history_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.history_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.history_table.setColumnWidth(5, 250)
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.verticalHeader().setDefaultSectionSize(40)
        self.history_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.history_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.history_table.setStyleSheet("""
            QTableWidget {
                background-color: #04050a;
                border: 1px solid #16192a;
                border-radius: 8px;
                gridline-color: #0d0f1b;
                color: #e2e8f0;
            }
            QHeaderView::section {
                background-color: #06070e;
                color: #00f0ff;
                font-weight: 800;
                padding: 7px;
                border: 1px solid #141728;
                font-size: 11px;
                letter-spacing: 0.5px;
            }
        """)
        layout.addWidget(self.history_table)
        return tab

    def load_history_table(self):
        if not hasattr(self, 'history_table'):
            return
        records = self.history_manager.load_records()
        query = getattr(self, 'history_search_input', None)
        filter_text = query.text().strip().lower() if query else ""

        filtered = []
        for r in records:
            if not filter_text:
                filtered.append(r)
            else:
                combined = f"{r.get('title','')} {r.get('url','')} {r.get('tool','')} {r.get('status','')}".lower()
                if filter_text in combined:
                    filtered.append(r)

        self.history_table.setRowCount(len(filtered))
        for row, r in enumerate(filtered):
            self.history_table.setRowHeight(row, 40)
            self.history_table.setItem(row, 0, QTableWidgetItem(r.get("timestamp", "")))

            title_item = QTableWidgetItem(r.get("title", ""))
            title_item.setToolTip(r.get("url", ""))
            self.history_table.setItem(row, 1, title_item)

            self.history_table.setItem(row, 2, QTableWidgetItem(r.get("tool", "")))
            self.history_table.setItem(row, 3, QTableWidgetItem(r.get("file_size", "-")))

            is_ok = r.get("status") == "completed"
            status_str = "✔ Completed" if is_ok else "❌ Failed"
            st_item = QTableWidgetItem(status_str)
            st_item.setForeground(QColor("#10b981") if is_ok else QColor("#ef4444"))
            self.history_table.setItem(row, 4, st_item)

            act_widget = QWidget()
            act_layout = QHBoxLayout(act_widget)
            act_layout.setContentsMargins(4, 4, 4, 4)
            act_layout.setSpacing(6)
            act_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            file_path = r.get("file_path", "")
            export_dir = r.get("export_dir", "")
            url = r.get("url", "")

            if file_path and os.path.exists(file_path):
                open_file_btn = QPushButton("▶ Open")
                open_file_btn.setFixedHeight(24)
                open_file_btn.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(0, 240, 255, 0.12);
                        color: #00f0ff;
                        border: 1px solid #00f0ff;
                        border-radius: 5px;
                        padding: 2px 10px;
                        font-weight: 700;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: #00f0ff;
                        color: #000000;
                    }
                """)
                open_file_btn.setToolTip(f"Open media file: {os.path.basename(file_path)}")
                open_file_btn.clicked.connect(lambda ch, p=file_path: os.startfile(p))
                act_layout.addWidget(open_file_btn)

            if export_dir and os.path.exists(export_dir):
                open_dir_btn = QPushButton("📂 Folder")
                open_dir_btn.setFixedHeight(24)
                open_dir_btn.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(168, 85, 247, 0.12);
                        color: #c084fc;
                        border: 1px solid #a855f7;
                        border-radius: 5px;
                        padding: 2px 10px;
                        font-weight: 700;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: #a855f7;
                        color: #ffffff;
                    }
                """)
                open_dir_btn.setToolTip(f"Open directory: {export_dir}")
                open_dir_btn.clicked.connect(lambda ch, d=export_dir: os.startfile(d))
                act_layout.addWidget(open_dir_btn)

            copy_btn = QPushButton("📋 URL")
            copy_btn.setFixedHeight(24)
            copy_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(245, 158, 11, 0.12);
                    color: #fbbf24;
                    border: 1px solid #f59e0b;
                    border-radius: 5px;
                    padding: 2px 10px;
                    font-weight: 700;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #f59e0b;
                    color: #000000;
                }
            """)
            copy_btn.setToolTip("Copy source URL to clipboard")
            copy_btn.clicked.connect(lambda ch, u=url: QApplication.clipboard().setText(u))
            act_layout.addWidget(copy_btn)

            act_layout.addStretch()
            self.history_table.setCellWidget(row, 5, act_widget)

    def filter_history_table(self, text):
        self.load_history_table()

    def on_clear_history(self):
        reply = CyberMessageBox.show_question(self, "Clear History", "Are you sure you want to clear all download ingest history?")
        if reply:
            self.history_manager.clear_history()
            self.load_history_table()

    def connect_auto_save_signals(self):
        # aria2c tab
        self.aria_conn_spin.valueChanged.connect(self.save_active_profile_tab_settings)
        self.aria_split_spin.valueChanged.connect(self.save_active_profile_tab_settings)
        self.aria_speed_input.textChanged.connect(self.save_active_profile_tab_settings)
        self.aria_flags_input.textChanged.connect(self.save_active_profile_tab_settings)
        
        # yt-dlp tab
        self.ytdlp_fmt_combo.currentTextChanged.connect(self.save_active_profile_tab_settings)
        self.ytdlp_video_fmt.currentTextChanged.connect(self.save_active_profile_tab_settings)
        self.ytdlp_audio_cb.toggled.connect(self.save_active_profile_tab_settings)
        self.ytdlp_audio_fmt.currentTextChanged.connect(self.save_active_profile_tab_settings)
        self.ytdlp_audio_q.valueChanged.connect(self.save_active_profile_tab_settings)
        self.ytdlp_subs_cb.toggled.connect(self.save_active_profile_tab_settings)
        self.ytdlp_premiere_cb.toggled.connect(self.save_active_profile_tab_settings)
        self.ytdlp_cookie_combo.currentTextChanged.connect(self.save_active_profile_tab_settings)
        self.ytdlp_cookie_input.textChanged.connect(self.save_active_profile_tab_settings)
        self.ytdlp_proxy_input.textChanged.connect(self.save_active_profile_tab_settings)
        self.ytdlp_sleep_input.textChanged.connect(self.save_active_profile_tab_settings)
        self.ytdlp_flags_input.textChanged.connect(self.save_active_profile_tab_settings)
        
        # gallery-dl tab
        self.gallerydl_flags_input.textChanged.connect(self.save_active_profile_tab_settings)
        
        # spotdl tab
        self.spotdl_audio_fmt.currentTextChanged.connect(self.save_active_profile_tab_settings)
        self.spotdl_audio_q.currentTextChanged.connect(self.save_active_profile_tab_settings)
        self.spotdl_flags_input.textChanged.connect(self.save_active_profile_tab_settings)
        
        # instagram tab
        self.instagram_pics_cb.toggled.connect(self.save_active_profile_tab_settings)
        self.instagram_vids_cb.toggled.connect(self.save_active_profile_tab_settings)
        self.instagram_meta_cb.toggled.connect(self.save_active_profile_tab_settings)
        self.instagram_comments_cb.toggled.connect(self.save_active_profile_tab_settings)
        self.instagram_format_combo.currentTextChanged.connect(self.save_active_profile_tab_settings)
        self.instagram_flags_input.textChanged.connect(self.save_active_profile_tab_settings)

    def save_active_profile_tab_settings(self):
        if self.is_loading_profile:
            return

        active_prof = self.config_manager.get_active_profile()
        if not active_prof:
            return

        # 1. Update aria2 settings
        aria_settings = {
            "max_connection_per_server": self.aria_conn_spin.value(),
            "split": self.aria_split_spin.value(),
            "max_download_limit": self.aria_speed_input.text().strip(),
            "custom_flags": self.aria_flags_input.text().strip()
        }
        active_prof["aria2_settings"] = aria_settings

        # 2. Update yt-dlp settings
        fmt_text = self.ytdlp_fmt_combo.currentText()
        fmt = fmt_text.split(" ")[0]

        cookie_text = self.ytdlp_cookie_combo.currentText()
        if "None" in cookie_text:
            cookie_source = "none"
        elif "Custom" in cookie_text:
            cookie_source = "custom"
        else:
            cookie_source = cookie_text.lower()

        ytdlp_settings = {
            "format": fmt,
            "video_format": self.ytdlp_video_fmt.currentText(),
            "extract_audio": self.ytdlp_audio_cb.isChecked(),
            "audio_format": self.ytdlp_audio_fmt.currentText(),
            "audio_quality": str(self.ytdlp_audio_q.value()),
            "embed_subs": self.ytdlp_subs_cb.isChecked(),
            "premiere_compatible": self.ytdlp_premiere_cb.isChecked(),
            "cookie_source": cookie_source,
            "cookie_file": self.ytdlp_cookie_input.text().strip(),
            "proxy": self.ytdlp_proxy_input.text().strip(),
            "sleep_requests": self.ytdlp_sleep_input.text().strip(),
            "custom_flags": self.ytdlp_flags_input.text().strip()
        }
        active_prof["ytdlp_settings"] = ytdlp_settings

        # 3. Update gallery-dl settings
        gallerydl_settings = {
            "custom_flags": self.gallerydl_flags_input.text().strip()
        }
        active_prof["gallerydl_settings"] = gallerydl_settings

        # 4. Update spotdl settings
        spotdl_settings = {
            "audio_format": self.spotdl_audio_fmt.currentText(),
            "audio_quality": self.spotdl_audio_q.currentText(),
            "custom_flags": self.spotdl_flags_input.text().strip()
        }
        active_prof["spotdl_settings"] = spotdl_settings

        # 5. Update instagram settings
        fmt_val = self.instagram_format_combo.currentText()
        if "mp4" in fmt_val:
            out_type = "video_mp4"
        elif "m4a" in fmt_val:
            out_type = "audio_m4a"
        else:
            out_type = "audio_mp3"

        instagram_settings = {
            "download_pictures": self.instagram_pics_cb.isChecked(),
            "download_videos": self.instagram_vids_cb.isChecked(),
            "download_metadata": self.instagram_meta_cb.isChecked(),
            "download_comments": self.instagram_comments_cb.isChecked(),
            "output_type": out_type,
            "custom_flags": self.instagram_flags_input.text().strip()
        }
        active_prof["instagram_settings"] = instagram_settings

        self.config_manager.save()

    # ----------------- PROFILES LOGIC -----------------
    def load_profiles(self):
        self.profiles_list.blockSignals(True)
        self.profiles_list.clear()
        
        profiles = self.config_manager.get_profiles()
        active_name = self.config_manager.get_active_profile_name()
        
        root_profiles = []
        folder_groups = {}
        
        for p in profiles:
            folder = p.get("folder", "")
            if not folder:
                root_profiles.append(p)
            else:
                if folder not in folder_groups:
                    folder_groups[folder] = []
                folder_groups[folder].append(p)
        
        active_item = None
        
        for folder_name, folder_profs in sorted(folder_groups.items()):
            folder_item = QTreeWidgetItem(self.profiles_list)
            folder_item.setText(0, f"📁 {folder_name}")
            folder_item.setData(0, Qt.ItemDataRole.UserRole, "folder")
            folder_item.setData(0, Qt.ItemDataRole.UserRole + 1, folder_name)
            
            if folder_name in self.expanded_folders:
                folder_item.setExpanded(True)
            
            for p in folder_profs:
                child_item = QTreeWidgetItem(folder_item)
                child_item.setText(0, f"⚡ {p['name']}")
                child_item.setData(0, Qt.ItemDataRole.UserRole, "profile")
                child_item.setData(0, Qt.ItemDataRole.UserRole + 1, p["name"])
                
                if p["name"] == active_name:
                    active_item = child_item
                    
        for p in root_profiles:
            root_item = QTreeWidgetItem(self.profiles_list)
            root_item.setText(0, f"⚡ {p['name']}")
            root_item.setData(0, Qt.ItemDataRole.UserRole, "profile")
            root_item.setData(0, Qt.ItemDataRole.UserRole + 1, p["name"])
            
            if p["name"] == active_name:
                active_item = root_item
                
        if active_item:
            self.profiles_list.setCurrentItem(active_item)
            parent = active_item.parent()
            if parent:
                parent.setExpanded(True)
                self.expanded_folders.add(parent.data(0, Qt.ItemDataRole.UserRole + 1))
                
        self.profiles_list.blockSignals(False)
        self.display_active_profile_details()

    def update_folder_combobox(self):
        self.prof_folder_input.blockSignals(True)
        self.prof_folder_input.clear()
        self.prof_folder_input.addItem("")
        
        folders = set()
        for p in self.config_manager.get_profiles():
            f = p.get("folder", "")
            if f:
                folders.add(f)
                
        for f in sorted(folders):
            self.prof_folder_input.addItem(f)
            
        self.prof_folder_input.blockSignals(False)

    def display_active_profile_details(self):
        active_prof = self.config_manager.get_active_profile()
        if not active_prof:
            return

        self.is_loading_profile = True

        self.prof_name_input.setText(active_prof["name"])
        self.update_folder_combobox()
        self.prof_folder_input.setCurrentText(active_prof.get("folder", ""))
        self.prof_tool_combo.setCurrentText(active_prof["tool"])
        use_custom = active_prof.get("use_custom_path", False)
        self.prof_auto_path_cb.setChecked(not use_custom)
        self.update_profile_export_dir_preview()

        tool = active_prof["tool"]
        if tool == "yt-dlp":
            self.config_tabs.setCurrentIndex(0)
            ytdlp_s = active_prof.get("ytdlp_settings", {})
            fmt = ytdlp_s.get("format", "bestvideo+bestaudio/best")
            
            idx = 0
            for i in range(self.ytdlp_fmt_combo.count()):
                if self.ytdlp_fmt_combo.itemText(i).startswith(fmt):
                    idx = i
                    break
            self.ytdlp_fmt_combo.setCurrentIndex(idx)
            
            self.ytdlp_video_fmt.setCurrentText(ytdlp_s.get("video_format", "best"))
            self.ytdlp_audio_cb.setChecked(ytdlp_s.get("extract_audio", False))
            self.ytdlp_audio_fmt.setCurrentText(ytdlp_s.get("audio_format", "mp3"))
            self.ytdlp_audio_q.setValue(int(ytdlp_s.get("audio_quality", 5)))
            self.ytdlp_subs_cb.setChecked(ytdlp_s.get("embed_subs", True))
            self.ytdlp_premiere_cb.setChecked(ytdlp_s.get("premiere_compatible", True))
            
            cookie_src = ytdlp_s.get("cookie_source", "none").capitalize()
            if cookie_src == "None":
                self.ytdlp_cookie_combo.setCurrentText("None (Anonymous)")
            elif cookie_src == "Custom":
                self.ytdlp_cookie_combo.setCurrentText("Custom cookies.txt File")
            else:
                idx = self.ytdlp_cookie_combo.findText(cookie_src)
                if idx >= 0:
                    self.ytdlp_cookie_combo.setCurrentIndex(idx)
                else:
                    self.ytdlp_cookie_combo.setCurrentText("None (Anonymous)")

            self.ytdlp_cookie_input.setText(ytdlp_s.get("cookie_file", ""))
            self.ytdlp_proxy_input.setText(ytdlp_s.get("proxy", ""))
            self.ytdlp_sleep_input.setText(str(ytdlp_s.get("sleep_requests", "")))
            self.ytdlp_flags_input.setText(ytdlp_s.get("custom_flags", ""))

            is_audio = ytdlp_s.get("extract_audio", False)
            self.ytdlp_video_lbl.setEnabled(not is_audio)
            self.ytdlp_video_fmt.setEnabled(not is_audio)
        elif tool == "aria2c":
            self.config_tabs.setCurrentIndex(1)
            aria_s = active_prof.get("aria2_settings", {})
            self.aria_conn_spin.setValue(aria_s.get("max_connection_per_server", 16))
            self.aria_split_spin.setValue(aria_s.get("split", 16))
            self.aria_speed_input.setText(aria_s.get("max_download_limit", "0"))
            self.aria_flags_input.setText(aria_s.get("custom_flags", ""))
        elif tool == "spotdl":
            self.config_tabs.setCurrentIndex(2)
            sdl_s = active_prof.get("spotdl_settings", {})
            self.spotdl_audio_fmt.setCurrentText(sdl_s.get("audio_format", "mp3"))
            sdl_q = sdl_s.get("audio_quality", "auto")
            if sdl_q == "best":
                sdl_q = "auto"
            self.spotdl_audio_q.setCurrentText(sdl_q)
            self.spotdl_flags_input.setText(sdl_s.get("custom_flags", ""))
        elif tool == "instagram":
            self.config_tabs.setCurrentIndex(3)
            ig_s = active_prof.get("instagram_settings", {})
            self.instagram_pics_cb.setChecked(ig_s.get("download_pictures", True))
            self.instagram_vids_cb.setChecked(ig_s.get("download_videos", True))
            self.instagram_meta_cb.setChecked(ig_s.get("download_metadata", False))
            self.instagram_comments_cb.setChecked(ig_s.get("download_comments", False))
            
            out_type = ig_s.get("output_type", "video_mp4")
            if out_type == "video_mp4":
                self.instagram_format_combo.setCurrentText("Video (mp4)")
            elif out_type == "audio_m4a":
                self.instagram_format_combo.setCurrentText("Audio Only (m4a)")
            else:
                self.instagram_format_combo.setCurrentText("Audio Only (mp3)")
                
            self.instagram_flags_input.setText(ig_s.get("custom_flags", ""))
        elif tool == "gallery-dl":
            self.config_tabs.setCurrentIndex(4)
            gdl_s = active_prof.get("gallerydl_settings", {})
            self.gallerydl_flags_input.setText(gdl_s.get("custom_flags", ""))

        self.is_loading_profile = False

    def on_profile_item_clicked(self, item, column):
        role = item.data(0, Qt.ItemDataRole.UserRole)
        if role == "profile":
            profile_name = item.data(0, Qt.ItemDataRole.UserRole + 1)
            self.config_manager.set_active_profile(profile_name)
            self.display_active_profile_details()

    def on_folder_expanded(self, item):
        role = item.data(0, Qt.ItemDataRole.UserRole)
        if role == "folder":
            folder_name = item.data(0, Qt.ItemDataRole.UserRole + 1)
            self.expanded_folders.add(folder_name)

    def on_folder_collapsed(self, item):
        role = item.data(0, Qt.ItemDataRole.UserRole)
        if role == "folder":
            folder_name = item.data(0, Qt.ItemDataRole.UserRole + 1)
            self.expanded_folders.discard(folder_name)

    def on_profile_moved(self, profile_name, new_folder):
        for p in self.config_manager.get_profiles():
            if p["name"] == profile_name:
                p["folder"] = new_folder
                self.config_manager.ensure_profile_export_dir(p)
                break
        self.config_manager.save()
        QTimer.singleShot(0, self.load_profiles)

    def on_add_folder(self):
        folder_name, ok = CyberInputDialog.get_text(self, "Create Folder", "Enter new folder group name:")
        if not ok or not folder_name:
            return
        
        existing_folders = set()
        for p in self.config_manager.get_profiles():
            f = p.get("folder", "")
            if f:
                existing_folders.add(f)
                
        if folder_name in existing_folders:
            CyberMessageBox.show_info(self, "Duplicate Folder", f"A folder group named '{folder_name}' already exists.", border_color="#ff007f")
            return
            
        profiles = self.config_manager.get_profiles()
        idx = 1
        profile_name = f"Profile in {folder_name}"
        existing_names = [p["name"] for p in profiles]
        while profile_name in existing_names:
            idx += 1
            profile_name = f"Profile in {folder_name} {idx}"

        new_profile = {
            "name": profile_name,
            "tool": "yt-dlp",
            "folder": folder_name,
            "use_custom_path": False,
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
                "extract_audio": False,
                "embed_subs": True,
                "premiere_compatible": True,
                "custom_flags": ""
            },
            "gallerydl_settings": {"custom_flags": ""},
            "spotdl_settings": {"audio_format": "mp3", "audio_quality": "auto", "custom_flags": ""},
            "instagram_settings": {"download_pictures": True, "download_videos": True, "download_metadata": False, "download_comments": False, "output_type": "video_mp4", "custom_flags": ""}
        }
        
        self.config_manager.ensure_folder_dir(folder_name)
        self.config_manager.add_profile(new_profile)
        self.config_manager.set_active_profile(profile_name)
        self.expanded_folders.add(folder_name)
        self.load_profiles()

    def on_add_profile(self, target_folder=None):
        default_folder = target_folder or ""
        if not default_folder:
            curr_item = self.profiles_list.currentItem()
            if curr_item:
                role = curr_item.data(0, Qt.ItemDataRole.UserRole)
                if role == "folder":
                    default_folder = curr_item.data(0, Qt.ItemDataRole.UserRole + 1)
                elif role == "profile":
                    parent = curr_item.parent()
                    if parent:
                        default_folder = parent.data(0, Qt.ItemDataRole.UserRole + 1)

        if not default_folder:
            default_folder = "Nexus Ingest"

        profiles = self.config_manager.get_profiles()
        idx = 1
        name = f"Custom Profile {idx}"
        existing_names = [p["name"] for p in profiles]
        while name in existing_names:
            idx += 1
            name = f"Custom Profile {idx}"

        new_profile = {
            "name": name,
            "tool": "yt-dlp",
            "folder": default_folder,
            "use_custom_path": False,
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
                "extract_audio": False,
                "embed_subs": True,
                "premiere_compatible": True,
                "custom_flags": ""
            },
            "gallerydl_settings": {"custom_flags": ""},
            "spotdl_settings": {"audio_format": "mp3", "audio_quality": "auto", "custom_flags": ""},
            "instagram_settings": {"download_pictures": True, "download_videos": True, "download_metadata": False, "download_comments": False, "output_type": "video_mp4", "custom_flags": ""}
        }
        
        self.config_manager.add_profile(new_profile)
        self.config_manager.set_active_profile(name)
        self.load_profiles()

    def on_delete_profile(self):
        curr_item = self.profiles_list.currentItem()
        if not curr_item:
            return

        role = curr_item.data(0, Qt.ItemDataRole.UserRole)
        if role == "folder":
            folder_name = curr_item.data(0, Qt.ItemDataRole.UserRole + 1)
            profs_in_folder = [p for p in self.config_manager.get_profiles() if p.get("folder", "") == folder_name]
            
            reply = CyberMessageBox.show_question(
                self, "Confirm Delete Folder",
                f"Are you sure you want to delete folder '{folder_name}' and all of its {len(profs_in_folder)} profiles?"
            )
            if reply:
                for p in profs_in_folder:
                    self.config_manager.delete_profile(p["name"])
                self.load_profiles()
        elif role == "profile":
            current_name = curr_item.data(0, Qt.ItemDataRole.UserRole + 1)
            
            if len(self.config_manager.get_profiles()) <= 1:
                CyberMessageBox.show_info(self, "Cannot Delete", "You must keep at least one profile.", border_color="#ff007f")
                return

            reply = CyberMessageBox.show_question(
                self, "Confirm Delete",
                f"Are you sure you want to delete profile '{current_name}'?"
            )
            if reply:
                self.config_manager.delete_profile(current_name)
                self.load_profiles()

    def on_open_cookie_manager(self):
        dlg = CookieManagerDialog(self)
        dlg.exec()
        self.update_cookie_header_badge()

    def update_cookie_header_badge(self):
        from downloader import get_cookie_status
        has_cookies, count, _ = get_cookie_status("cookies.txt")
        if has_cookies:
            self.cookie_manager_btn.setText(f"Cookies Active ({count})")
            self.cookie_manager_btn.setStyleSheet("""
                background-color: #064e3b;
                color: #34d399;
                border: 1px solid #10b981;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
            """)
        else:
            self.cookie_manager_btn.setText("Cookie Manager")
            self.cookie_manager_btn.setStyleSheet("""
                background-color: #1e293b;
                color: #fbbf24;
                border: 1px solid #fbbf24;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
            """)

    def on_browse_cookie_file(self):
        selected_file, _ = QFileDialog.getOpenFileName(
            self, "Select cookies.txt file", os.path.expanduser("~"), "Text / Cookie Files (*.txt *.cookies);;All Files (*.*)"
        )
        if selected_file:
            self.ytdlp_cookie_input.setText(selected_file.replace("/", "\\"))
            self.ytdlp_cookie_combo.setCurrentText("Custom cookies.txt File")

    def on_browse_directory(self):
        current_dir = self.prof_dir_input.text()
        if not os.path.exists(current_dir):
            current_dir = self.config_manager.get_main_library_dir()
            
        selected_dir = QFileDialog.getExistingDirectory(
            self, "Select Download Destination Folder", current_dir
        )
        if selected_dir:
            self.prof_dir_input.setText(os.path.normpath(selected_dir))

    def on_open_current_export_dir(self):
        active_prof = self.config_manager.get_active_profile()
        if active_prof:
            path = self.config_manager.ensure_profile_export_dir(active_prof)
            if os.path.exists(path):
                os.startfile(path)
            else:
                CyberMessageBox.show_info(self, "Directory Not Found", f"Folder does not exist yet: {path}")

    def on_tool_combo_changed(self, tool_name):
        if tool_name == "yt-dlp":
            self.config_tabs.setCurrentIndex(0)
        elif tool_name == "aria2c":
            self.config_tabs.setCurrentIndex(1)
        elif tool_name == "spotdl":
            self.config_tabs.setCurrentIndex(2)
        elif tool_name == "instagram":
            self.config_tabs.setCurrentIndex(3)
        elif tool_name == "gallery-dl":
            self.config_tabs.setCurrentIndex(4)

    def on_ytdlp_audio_toggled(self, checked):
        self.ytdlp_audio_fmt.setEnabled(checked)
        self.ytdlp_audio_q.setEnabled(checked)
        self.ytdlp_video_lbl.setEnabled(not checked)
        self.ytdlp_video_fmt.setEnabled(not checked)

    def on_save_profile_settings(self):
        active_name = self.config_manager.get_active_profile_name()
        if not active_name:
            return

        new_name = self.prof_name_input.text().strip()
        if not new_name:
            CyberMessageBox.show_info(self, "Invalid Name", "Profile name cannot be empty.", border_color="#ff007f")
            return

        if new_name != active_name:
            existing = [p["name"] for p in self.config_manager.get_profiles() if p["name"] != active_name]
            if new_name in existing:
                CyberMessageBox.show_info(self, "Duplicate Name", f"A profile named '{new_name}' already exists.", border_color="#ff007f")
                return

        tool = self.prof_tool_combo.currentText()
        folder = self.prof_folder_input.currentText().strip()
        
        is_auto = self.prof_auto_path_cb.isChecked()
        use_custom_path = not is_auto
        if use_custom_path:
            export_dir = self.prof_dir_input.text().strip()
        else:
            export_dir = ""

        aria_settings = {
            "max_connection_per_server": self.aria_conn_spin.value(),
            "split": self.aria_split_spin.value(),
            "max_download_limit": self.aria_speed_input.text().strip(),
            "custom_flags": self.aria_flags_input.text().strip()
        }

        fmt_text = self.ytdlp_fmt_combo.currentText()
        fmt = fmt_text.split(" ")[0]

        cookie_text = self.ytdlp_cookie_combo.currentText()
        if "None" in cookie_text:
            cookie_source = "none"
        elif "Custom" in cookie_text:
            cookie_source = "custom"
        else:
            cookie_source = cookie_text.lower()

        ytdlp_settings = {
            "format": fmt,
            "video_format": self.ytdlp_video_fmt.currentText(),
            "extract_audio": self.ytdlp_audio_cb.isChecked(),
            "audio_format": self.ytdlp_audio_fmt.currentText(),
            "audio_quality": str(self.ytdlp_audio_q.value()),
            "embed_subs": self.ytdlp_subs_cb.isChecked(),
            "premiere_compatible": self.ytdlp_premiere_cb.isChecked(),
            "cookie_source": cookie_source,
            "cookie_file": self.ytdlp_cookie_input.text().strip(),
            "proxy": self.ytdlp_proxy_input.text().strip(),
            "sleep_requests": self.ytdlp_sleep_input.text().strip(),
            "custom_flags": self.ytdlp_flags_input.text().strip()
        }

        gallerydl_settings = {"custom_flags": self.gallerydl_flags_input.text().strip()}
        spotdl_settings = {
            "audio_format": self.spotdl_audio_fmt.currentText(),
            "audio_quality": self.spotdl_audio_q.currentText(),
            "custom_flags": self.spotdl_flags_input.text().strip()
        }
        instagram_settings = {
            "download_pictures": self.instagram_pics_cb.isChecked(),
            "download_videos": self.instagram_vids_cb.isChecked(),
            "download_metadata": self.instagram_meta_cb.isChecked(),
            "download_comments": self.instagram_comments_cb.isChecked(),
            "custom_flags": self.instagram_flags_input.text().strip()
        }

        updated_profile = {
            "name": new_name,
            "tool": tool,
            "folder": folder,
            "use_custom_path": use_custom_path,
            "export_dir": export_dir,
            "aria2_settings": aria_settings,
            "ytdlp_settings": ytdlp_settings,
            "gallerydl_settings": gallerydl_settings,
            "spotdl_settings": spotdl_settings,
            "instagram_settings": instagram_settings
        }

        self.config_manager.update_profile(active_name, updated_profile)
        final_dir = self.config_manager.ensure_profile_export_dir(updated_profile)
        self.load_profiles()
        CyberMessageBox.show_info(self, "Settings Saved", f"Profile '{new_name}' saved successfully.\nDestination: {final_dir}", border_color="#00f0ff")

    # ----------------- MAIN INGEST ROOT & AUTO PATHS -----------------
    def on_change_main_library_dir(self):
        curr_dir = self.config_manager.get_main_library_dir()
        selected_dir = QFileDialog.getExistingDirectory(
            self, "Select Main Ingest Library Root Folder", curr_dir
        )
        if selected_dir:
            clean_dir = os.path.normpath(selected_dir)
            self.config_manager.set_main_library_dir(clean_dir)
            self.update_main_library_label()
            if hasattr(self, "tuning_lib_dir_input"):
                self.tuning_lib_dir_input.setText(clean_dir)
            self.update_profile_export_dir_preview()
            for p in self.config_manager.get_profiles():
                self.config_manager.ensure_profile_export_dir(p)
            CyberMessageBox.show_info(
                self, "Library Root Updated",
                f"Main ingest root directory set to:\n{clean_dir}\n\nAuto-managed profiles will store media within this hierarchy.",
                border_color="#00f0ff"
            )

    def on_open_main_library_dir(self):
        dir_path = self.config_manager.get_main_library_dir()
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        os.startfile(dir_path)

    def update_main_library_label(self):
        root_path = self.config_manager.get_main_library_dir()
        if hasattr(self, "main_library_lbl"):
            self.main_library_lbl.setText(root_path)
            self.main_library_lbl.setToolTip(f"Current Main Ingest Root Folder:\n{root_path}")

    def update_profile_export_dir_preview(self):
        active_prof = self.config_manager.get_active_profile()
        if not active_prof:
            return

        is_auto = self.prof_auto_path_cb.isChecked()
        if is_auto:
            mock_p = {
                "name": self.prof_name_input.text().strip() or active_prof["name"],
                "folder": self.prof_folder_input.currentText().strip(),
                "use_custom_path": False,
                "export_dir": ""
            }
            resolved = self.config_manager.resolve_profile_export_dir(mock_p)
            self.prof_dir_input.setText(resolved)
            self.prof_dir_input.setReadOnly(True)
            self.prof_dir_input.setStyleSheet("color: #00f0ff; background-color: #0a0e1a; border: 1px solid #142038;")
            self.prof_dir_btn.setEnabled(False)
            self.prof_dir_btn.setToolTip("Path auto-mirrors folder hierarchy")
        else:
            self.prof_dir_input.setReadOnly(False)
            self.prof_dir_input.setStyleSheet("")
            custom_dir = active_prof.get("export_dir", "") or self.config_manager.get_main_library_dir()
            self.prof_dir_input.setText(custom_dir)
            self.prof_dir_btn.setEnabled(True)
            self.prof_dir_btn.setToolTip("Browse custom export directory")

        # Update sidebar snapshot card & armed banner in Ingest & Queue
        prof_name = active_prof.get("name", "Default")
        prof_tool = active_prof.get("tool", "yt-dlp")
        disp_dir = self.prof_dir_input.text() if hasattr(self, "prof_dir_input") else ""

        if hasattr(self, "snapshot_name_lbl"):
            self.snapshot_name_lbl.setText(prof_name)
        if hasattr(self, "snapshot_tool_badge"):
            self.snapshot_tool_badge.setText(prof_tool)
        if hasattr(self, "snapshot_path_lbl"):
            self.snapshot_path_lbl.setText(disp_dir)
            self.snapshot_path_lbl.setToolTip(f"Export Path:\n{disp_dir}")

        if hasattr(self, "armed_profile_lbl"):
            self.armed_profile_lbl.setText(
                f"🎯 ARMED PROFILE: <b style='color:#ffffff;'>{prof_name}</b>  |  "
                f"ENGINE: <b style='color:#00f0ff;'>{prof_tool}</b>  |  "
                f"FOLDER: <span style='color:#94a3b8; font-family:monospace;'>{disp_dir}</span>"
            )

    def on_auto_path_toggled(self, checked):
        if not self.is_loading_profile:
            self.update_profile_export_dir_preview()

    def on_profile_form_field_changed(self, text=""):
        if not self.is_loading_profile and self.prof_auto_path_cb.isChecked():
            self.update_profile_export_dir_preview()

    def on_profile_tree_context_menu(self, pos):
        item = self.profiles_list.itemAt(pos)
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #0a0d18;
                color: #e2e8f0;
                border: 1px solid #00f0ff;
                border-radius: 8px;
                padding: 6px;
            }
            QMenu::item {
                padding: 6px 16px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #1e2540;
                color: #00f0ff;
            }
            QMenu::separator {
                height: 1px;
                background-color: #1e2238;
                margin: 4px 8px;
            }
        """)

        if item:
            role = item.data(0, Qt.ItemDataRole.UserRole)
            target_name = item.data(0, Qt.ItemDataRole.UserRole + 1)
            if role == "folder":
                folder_name = target_name
                act_open = menu.addAction(f"📂 Open '{folder_name}' on Disk")
                act_open.triggered.connect(lambda: os.startfile(self.config_manager.ensure_folder_dir(folder_name)))

                act_add = menu.addAction(f"➕ Add Profile in '{folder_name}'")
                act_add.triggered.connect(lambda: self.add_profile_in_folder(folder_name))

                menu.addSeparator()
                act_export = menu.addAction(f"📤 Export Folder Package...")
                act_export.triggered.connect(lambda: self.on_export_profiles_action(scope="folder", scope_target=folder_name))

                menu.addSeparator()
                act_delete = menu.addAction(f"🗑️ Delete Folder '{folder_name}'")
                act_delete.triggered.connect(self.on_delete_profile)
            elif role == "profile":
                prof_name = target_name
                prof = next((p for p in self.config_manager.get_profiles() if p["name"] == prof_name), None)
                
                act_select = menu.addAction(f"⚡ Set as Active Profile")
                act_select.triggered.connect(lambda: (self.config_manager.set_active_profile(prof_name), self.display_active_profile_details()))

                if prof:
                    act_open = menu.addAction(f"📂 Open Destination on Disk")
                    act_open.triggered.connect(lambda: os.startfile(self.config_manager.ensure_profile_export_dir(prof)))

                menu.addSeparator()
                act_export = menu.addAction(f"📤 Export Profile Package...")
                act_export.triggered.connect(lambda: self.on_export_profiles_action(scope="profile", scope_target=prof_name))

                menu.addSeparator()
                act_delete = menu.addAction(f"🗑️ Delete Profile")
                act_delete.triggered.connect(self.on_delete_profile)
        else:
            act_new_prof = menu.addAction("➕ New Profile")
            act_new_prof.triggered.connect(self.on_add_profile)

            act_new_folder = menu.addAction("📁 New Folder Group")
            act_new_folder.triggered.connect(self.on_add_folder)

            menu.addSeparator()
            act_import = menu.addAction("📥 Import Profiles Package...")
            act_import.triggered.connect(self.on_import_profiles_action)

        menu.exec(self.profiles_list.viewport().mapToGlobal(pos))

    def add_profile_in_folder(self, folder_name):
        self.on_add_profile(target_folder=folder_name)

    def on_export_profiles_action(self, scope="all", scope_target=None):
        if scope == "folder" and scope_target:
            default_fn = f"nexus_{scope_target.lower().replace(' ', '_')}_profiles.nexus"
            title = f"Export Folder '{scope_target}'"
        elif scope == "profile" and scope_target:
            default_fn = f"nexus_{scope_target.lower().replace(' ', '_')}.nexus"
            title = f"Export Profile '{scope_target}'"
        else:
            default_fn = "nexus_all_profiles.nexus"
            title = "Export All Profiles"

        file_path, _ = QFileDialog.getSaveFileName(
            self, title, default_fn, "Nexus Package (*.nexus);;JSON File (*.json);;All Files (*.*)"
        )
        if not file_path:
            return

        success, msg = self.config_manager.export_profiles(file_path, scope=scope, scope_target=scope_target)
        if success:
            CyberMessageBox.show_info(self, "Export Successful", msg, border_color="#00f0ff")
        else:
            CyberMessageBox.show_info(self, "Export Failed", msg, border_color="#ff007f")

    def on_import_profiles_action(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Profiles Package", "", "Nexus Packages (*.nexus *.json);;All Files (*.*)"
        )
        if not file_path:
            return

        choice = CyberChoiceDialog.get_choice(
            self, "Import Profiles",
            "How would you like to import these profiles?\n\n• MERGE: Keep existing profiles and add new ones\n• REPLACE: Overwrite all current profiles",
            opt1_text="Merge", opt2_text="Replace"
        )
        if not choice:
            return

        success, msg = self.config_manager.import_profiles(file_path, mode=choice)
        if success:
            self.load_profiles()
            self.display_active_profile_details()
            CyberMessageBox.show_info(self, "Import Complete", msg, border_color="#00f0ff")
        else:
            CyberMessageBox.show_info(self, "Import Failed", msg, border_color="#ff007f")

    # ----------------- TOOL DOWNLOADER & DIAGNOSTICS -----------------
    def refresh_tools_status(self):
        tools = ["yt-dlp", "aria2c", "ffmpeg", "spotdl", "gallery-dl", "instagram"]
        for t in tools:
            is_ins = self.dep_manager.is_installed(t)
            version = self.dep_manager.get_tool_version(t) if is_ins else None
            if is_ins:
                v_str = f"v{version}" if version and not version.startswith("v") else (version or "Installed")
                self.update_engine_card_status(t, "working", v_str, "Ready")
                self.update_engine_badge(t, "working", v_str)
            else:
                self.update_engine_card_status(t, "offline", "Missing", "Not Installed")
                self.update_engine_badge(t, "offline", "Missing")
        self.update_health_hud()

    def update_engine_badge(self, tool_name, status="working", detail=""):
        if tool_name not in self.engine_badges:
            return
        badge = self.engine_badges[tool_name]
        TOOL_LABELS = {
            "yt-dlp": "yt-dlp",
            "aria2c": "aria2c",
            "ffmpeg": "ffmpeg",
            "spotdl": "spotdl",
            "gallery-dl": "g-dl",
            "instagram": "insta"
        }
        short_label = TOOL_LABELS.get(tool_name, tool_name)
        badge.setText(f"{short_label} ●")
        badge.setProperty("status", status)
        badge.setToolTip(f"{tool_name}: {detail}\nClick to inspect in Engine Center")
        badge.style().unpolish(badge)
        badge.style().polish(badge)

    def update_engine_card_status(self, tool_name, status="working", version_str="Installed", detail_str="Operational"):
        if tool_name not in self.engine_widgets:
            return
        w_info = self.engine_widgets[tool_name]
        v_lbl = w_info.get("version_lbl")
        s_badge = w_info.get("status_badge")
        btn = w_info.get("btn")
        
        if v_lbl:
            v_lbl.setText(f"v{version_str}" if version_str and not version_str.startswith("v") and version_str != "Missing" else version_str)
        
        status_configs = {
            "working": ("🟢 Operational", "badge_working"),
            "warning": ("🟡 Warning", "badge_warning"),
            "outdated": ("🟣 Outdated", "badge_outdated"),
            "offline": ("🔴 Missing", "badge_offline")
        }
        label_txt, obj_name = status_configs.get(status, ("⚪ Unknown", "badge_offline"))
        if s_badge:
            s_badge.setText(label_txt)
            s_badge.setObjectName(obj_name)
            s_badge.setToolTip(detail_str)
            s_badge.style().unpolish(s_badge)
            s_badge.style().polish(s_badge)
        
        if btn:
            btn.setText("Update" if status != "offline" else "Download & Install")

    def update_health_hud(self):
        total = len(self.engine_badges)
        if total == 0:
            return
        working_count = 0
        for t, badge in self.engine_badges.items():
            if badge.property("status") == "working":
                working_count += 1
        if hasattr(self, "engine_health_hud"):
            if working_count == total:
                self.engine_health_hud.setText(f"🟢 {working_count}/{total} Operational")
                self.engine_health_hud.setStyleSheet("color: #00ff88; font-weight: 800; font-size: 11px; padding: 3px 9px; border: 1px solid rgba(0, 255, 136, 0.4); border-radius: 7px; background-color: rgba(0, 255, 136, 0.08);")
            elif working_count > 0:
                self.engine_health_hud.setText(f"🟡 {working_count}/{total} Operational")
                self.engine_health_hud.setStyleSheet("color: #fbbf24; font-weight: 800; font-size: 11px; padding: 3px 9px; border: 1px solid rgba(251, 191, 36, 0.4); border-radius: 7px; background-color: rgba(251, 191, 36, 0.08);")
            else:
                self.engine_health_hud.setText(f"🔴 0/{total} Engines Ready")
                self.engine_health_hud.setStyleSheet("color: #ff0055; font-weight: 800; font-size: 11px; padding: 3px 9px; border: 1px solid rgba(255, 0, 85, 0.4); border-radius: 7px; background-color: rgba(255, 0, 85, 0.08);")

    def quick_test_engine(self, tool_name):
        if tool_name in self.tool_diagnostic_workers and self.tool_diagnostic_workers[tool_name].isRunning():
            return
        if tool_name in self.engine_widgets:
            self.engine_widgets[tool_name]["test_btn"].setText("🧪 Testing...")
            self.engine_widgets[tool_name]["test_btn"].setEnabled(False)

        worker = ToolDiagnosticWorker(self.dep_manager, tool_name, self)
        worker.finished.connect(self.on_tool_diagnostic_finished)
        self.tool_diagnostic_workers[tool_name] = worker
        worker.start()

    @pyqtSlot(str, str, str)
    def on_tool_diagnostic_finished(self, tool_name, status, message):
        if tool_name in self.engine_widgets:
            self.engine_widgets[tool_name]["test_btn"].setText("🧪 Quick Test")
            self.engine_widgets[tool_name]["test_btn"].setEnabled(True)

        version = self.dep_manager.get_tool_version(tool_name) if self.dep_manager.is_installed(tool_name) else "Missing"
        self.update_engine_card_status(tool_name, status, version, message)
        self.update_engine_badge(tool_name, status, message)
        self.update_health_hud()

    def run_all_diagnostics(self):
        if self.batch_diagnostic_worker and self.batch_diagnostic_worker.isRunning():
            return
        self.run_all_diag_btn.setEnabled(False)
        self.run_all_diag_btn.setText("🧪 Running...")
        self.tool_progress_lbl.setText("Running quick diagnostics on all engines...")

        tools = ["yt-dlp", "aria2c", "ffmpeg", "spotdl", "gallery-dl", "instagram"]
        self.batch_diagnostic_worker = BatchToolDiagnosticWorker(self.dep_manager, tools, self)
        self.batch_diagnostic_worker.tool_tested.connect(self.on_batch_tool_tested)
        self.batch_diagnostic_worker.all_finished.connect(self.on_batch_diagnostics_finished)
        self.batch_diagnostic_worker.start()

    @pyqtSlot(str, str, str)
    def on_batch_tool_tested(self, tool_name, status, message):
        version = self.dep_manager.get_tool_version(tool_name) if self.dep_manager.is_installed(tool_name) else "Missing"
        self.update_engine_card_status(tool_name, status, version, message)
        self.update_engine_badge(tool_name, status, message)
        self.update_health_hud()

    @pyqtSlot(dict)
    def on_batch_diagnostics_finished(self, results):
        self.run_all_diag_btn.setEnabled(True)
        self.run_all_diag_btn.setText("🧪 Run All Diagnostics")
        self.tool_progress_lbl.setText("Diagnostics completed.")
        QTimer.singleShot(3000, lambda: self.tool_progress_lbl.setText(""))
        working_count = sum(1 for s, _ in results.values() if s == "working")
        CyberMessageBox.show_info(self, "Diagnostics Complete", f"Diagnostic suite completed: {working_count}/{len(results)} engines operational.", border_color="#00f0ff")

    def navigate_to_engine(self, tool_name):
        self.main_hub_tabs.setCurrentIndex(2)
        tool_map = {
            "yt-dlp": 0,
            "aria2c": 1,
            "spotdl": 2,
            "instagram": 3,
            "gallery-dl": 4
        }
        if tool_name in tool_map:
            self.config_tabs.setCurrentIndex(tool_map[tool_name])
        if tool_name in self.engine_widgets:
            card = self.engine_widgets[tool_name].get("card")
            if card:
                card.setStyleSheet("QFrame#engine_card { border: 2px solid #00f0ff; background-color: #0c1020; }")
                QTimer.singleShot(1500, lambda: card.setStyleSheet(""))

    def on_animations_toggled(self, checked):
        self.config_manager.set_enable_animations(checked)

    def on_clipboard_sniffer_toggled(self, checked):
        self.config_manager.set_clipboard_sniffer(checked)
        if not checked and hasattr(self, "clipboard_banner"):
            self.clipboard_banner.setVisible(False)

    def on_global_speed_changed(self, text):
        limit = text.split(" ")[0].strip()
        self.config_manager.set_global_speed_limit(limit)

    def on_clipboard_changed(self):
        if not self.config_manager.get_clipboard_sniffer():
            return
        try:
            text = self.clipboard.text().strip()
            if not text or text == self.last_sniffed_url:
                return
            if text.startswith("http://") or text.startswith("https://"):
                u_lower = text.lower()
                is_media = any(k in u_lower for k in [
                    "youtube.com", "youtu.be", "spotify.com", "instagram.com",
                    "twitter.com", "x.com", "tiktok.com", "soundcloud.com", "vimeo.com"
                ]) or any(u_lower.endswith(ext) for ext in [
                    ".mp4", ".mkv", ".mp3", ".flac", ".wav", ".webm", ".zip", ".tar.gz", ".iso"
                ])
                if is_media:
                    self.last_sniffed_url = text
                    self.show_clipboard_banner(text)
        except Exception:
            pass

    def show_clipboard_banner(self, url):
        display_url = url if len(url) <= 65 else url[:62] + "..."
        self.cb_msg_lbl.setText(f"📋 Media link detected: {display_url}")
        self.clipboard_banner.setVisible(True)

    def on_clipboard_ingest(self):
        if self.last_sniffed_url:
            curr = self.urls_input.toPlainText().strip()
            if curr:
                self.urls_input.setPlainText(curr + "\n" + self.last_sniffed_url)
            else:
                self.urls_input.setPlainText(self.last_sniffed_url)
            self.clipboard_banner.setVisible(False)
            self.start_download_batch()

    def update_all_engines(self):
        if self.batch_update_worker and self.batch_update_worker.isRunning():
            CyberMessageBox.show_info(self, "Updating", "Engine batch update is already in progress.", border_color="#ff007f")
            return
        if self.tool_download_workers:
            CyberMessageBox.show_info(self, "Busy", "An individual engine download is currently running.", border_color="#ff007f")
            return

        # Disable update buttons during batch operation
        self.quick_update_btn.setEnabled(False)
        if hasattr(self, 'update_all_tab_btn'):
            self.update_all_tab_btn.setEnabled(False)
        for t, w_info in self.engine_widgets.items():
            w_info["btn"].setEnabled(False)

        self.tool_progress_bar.setValue(0)
        self.tool_progress_bar.setVisible(True)
        self.tool_progress_lbl.setText("Starting engine updates...")

        tools_to_update = ["yt-dlp", "aria2c", "ffmpeg", "spotdl", "gallery-dl", "instagram"]
        self.batch_update_worker = BatchToolUpdateWorker(self.dep_manager, tools_to_update)
        self.batch_update_worker.overall_progress.connect(self.on_batch_update_progress)
        self.batch_update_worker.tool_finished.connect(self.on_batch_tool_finished)
        self.batch_update_worker.all_finished.connect(self.on_batch_all_finished)
        self.batch_update_worker.start()

    @pyqtSlot(int, int, str, float)
    def on_batch_update_progress(self, current_idx, total_count, current_tool, tool_percent):
        overall_percent = int(((current_idx - 1) / total_count) * 100 + (tool_percent / total_count))
        self.tool_progress_bar.setValue(overall_percent)
        self.tool_progress_lbl.setText(f"[{current_idx}/{total_count}] Updating {current_tool}... ({tool_percent:.0f}%)")

    @pyqtSlot(str, bool, str)
    def on_batch_tool_finished(self, tool_name, success, error_msg):
        is_ins = self.dep_manager.is_installed(tool_name)
        version = self.dep_manager.get_tool_version(tool_name) if is_ins else None
        status = "working" if is_ins else "offline"
        v_str = f"v{version}" if version and not version.startswith("v") else (version or "Installed")
        self.update_engine_card_status(tool_name, status, v_str, "Ready" if is_ins else "Missing")
        self.update_engine_badge(tool_name, status, v_str)
        self.update_health_hud()

    @pyqtSlot(list)
    def on_batch_all_finished(self, results):
        self.tool_progress_bar.setVisible(False)
        self.tool_progress_lbl.setText("")

        self.quick_update_btn.setEnabled(True)
        if hasattr(self, 'update_all_tab_btn'):
            self.update_all_tab_btn.setEnabled(True)
        for t, w_info in self.engine_widgets.items():
            w_info["btn"].setEnabled(True)

        if self.batch_update_worker:
            self.batch_update_worker.deleteLater()
            self.batch_update_worker = None

        self.refresh_tools_status()

        failures = [f"{t}: {err}" for t, ok, err in results if not ok]
        if not failures:
            CyberMessageBox.show_info(self, "Update Complete", "All engines were successfully updated to their latest versions!", border_color="#00f0ff")
        else:
            fail_text = "\n".join(failures)
            CyberMessageBox.show_info(self, "Update Notice", f"Engines updated with some errors:\n\n{fail_text}", border_color="#ff007f")

    def download_binary(self, tool_name, is_update=False):
        if self.batch_update_worker and self.batch_update_worker.isRunning():
            CyberMessageBox.show_info(self, "Busy", "Batch update is currently in progress.", border_color="#ff007f")
            return
        if tool_name in self.tool_download_workers:
            CyberMessageBox.show_info(self, "Downloading", f"Already downloading {tool_name}.", border_color="#ff007f")
            return

        if tool_name in self.engine_widgets:
            self.engine_widgets[tool_name]["btn"].setEnabled(False)

        self.tool_progress_bar.setValue(0)
        self.tool_progress_bar.setVisible(True)
        self.tool_progress_lbl.setText(f"Updating {tool_name} (0%)...")

        worker = ToolDownloadWorker(self.dep_manager, tool_name, is_update=is_update)
        worker.progress_updated.connect(self.on_tool_download_progress)
        worker.completed.connect(self.on_tool_download_completed)
        
        self.tool_download_workers[tool_name] = worker
        worker.start()

    @pyqtSlot(str, float)
    def on_tool_download_progress(self, tool_name, percentage):
        self.tool_progress_bar.setValue(int(percentage))
        self.tool_progress_lbl.setText(f"Updating {tool_name} ({percentage:.0f}%)...")

    @pyqtSlot(str, bool, str)
    def on_tool_download_completed(self, tool_name, success, error_msg):
        self.tool_progress_bar.setVisible(False)
        self.tool_progress_lbl.setText("")

        if tool_name in self.engine_widgets:
            self.engine_widgets[tool_name]["btn"].setEnabled(True)

        if tool_name in self.tool_download_workers:
            worker = self.tool_download_workers.pop(tool_name)
            worker.deleteLater()

        self.refresh_tools_status()

        if success:
            CyberMessageBox.show_info(self, "Update Complete", f"Successfully installed/updated {tool_name}.", border_color="#00f0ff")
        else:
            CyberMessageBox.show_info(self, "Install Error", f"Failed to install {tool_name}:\n{error_msg}", border_color="#ff007f")

    # ----------------- DOWNLOAD EXECUTION -----------------
    def on_paste_clipboard(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text().strip()
        if text:
            curr = self.urls_input.toPlainText().strip()
            if curr:
                self.urls_input.setPlainText(curr + "\n" + text)
            else:
                self.urls_input.setPlainText(text)

    def urls_input_clear(self):
        self.urls_input.clear()

    def start_download_batch(self):
        active_prof = self.config_manager.get_active_profile()
        if not active_prof:
            CyberMessageBox.show_info(self, "No Profile", "Please select a download profile first.", border_color="#ff007f")
            return

        tool_name = active_prof["tool"]

        urls_text = self.urls_input.toPlainText().strip()
        if not urls_text:
            CyberMessageBox.show_info(self, "No URLs", "Please enter or paste one or more URLs to download.", border_color="#ff007f")
            return

        urls = [line.strip() for line in urls_text.split("\n") if line.strip()]
        if not urls:
            CyberMessageBox.show_info(self, "No URLs", "No valid URLs found.", border_color="#ff007f")
            return

        self.urls_input.clear()
        export_dir = self.config_manager.ensure_profile_export_dir(active_prof)

        # Check for YouTube playlist/mix URLs and prompt user if needed
        remembered_choice = None
        sanitized_urls = []
        for raw_url in urls:
            url_to_add = raw_url
            is_yt, has_list, is_mix, is_pure_pl, single_url = inspect_youtube_url(raw_url)
            if has_list and not is_pure_pl:
                if remembered_choice == CyberPlaylistDialog.CHOICE_SINGLE:
                    url_to_add = single_url
                elif remembered_choice == CyberPlaylistDialog.CHOICE_PLAYLIST:
                    url_to_add = raw_url
                elif remembered_choice == CyberPlaylistDialog.CHOICE_CANCEL:
                    continue
                else:
                    dlg = CyberPlaylistDialog(raw_url, is_mix=is_mix, parent=self)
                    dlg.adjustSize()
                    geom = self.geometry()
                    x = geom.x() + (geom.width() - dlg.width()) // 2
                    y = geom.y() + (geom.height() - dlg.height()) // 2
                    dlg.move(x, y)
                    dlg.exec()
                    if dlg.choice == CyberPlaylistDialog.CHOICE_SINGLE:
                        url_to_add = single_url
                        if dlg.apply_to_all:
                            remembered_choice = dlg.choice
                    elif dlg.choice == CyberPlaylistDialog.CHOICE_PLAYLIST:
                        url_to_add = raw_url
                        if dlg.apply_to_all:
                            remembered_choice = dlg.choice
                    else:
                        if dlg.apply_to_all:
                            remembered_choice = dlg.choice
                        continue
            sanitized_urls.append(url_to_add)

        if not sanitized_urls:
            return

        # Switch to Queue tab immediately
        self.main_hub_tabs.setCurrentIndex(0)

        for url in sanitized_urls:
            download_id = str(uuid.uuid4())
            target_tool = tool_name
            
            if "spotify.com" in url.lower() or url.lower().startswith("spotify:"):
                target_tool = "spotdl"
            elif "instagram.com" in url.lower() and tool_name not in ["gallery-dl", "instagram"]:
                target_tool = "instagram"
                
            target_path = self.dep_manager.get_tool_path(target_tool)
            
            if target_tool == "aria2c":
                target_settings = active_prof.get("aria2_settings", {})
            elif target_tool == "yt-dlp":
                target_settings = active_prof.get("ytdlp_settings", {})
            elif target_tool == "gallery-dl":
                target_settings = active_prof.get("gallerydl_settings", {})
            elif target_tool == "spotdl":
                target_settings = active_prof.get("spotdl_settings", {})
            elif target_tool == "instagram":
                target_settings = active_prof.get("instagram_settings", {})
            else:
                target_settings = {}
                
            # Apply global speed limit if set and not explicitly overridden
            spd_limit = self.config_manager.get_global_speed_limit()
            if spd_limit and spd_limit != "0" and "max_download_limit" not in target_settings:
                target_settings["max_download_limit"] = spd_limit

            progress_card = DownloadProgressWidget(
                download_id, url, target_dir=export_dir,
                enable_animations=self.config_manager.get_enable_animations()
            )
            progress_card.cancelled.connect(self.cancel_download)
            progress_card.retry_requested.connect(self.retry_download)
            self.queue_list_layout.insertWidget(0, progress_card)

            if not target_path:
                progress_card.set_error(f"Missing engine: '{target_tool}'")
                self.on_download_log(download_id, f"[Nexus Ingest] [ERROR] The engine '{target_tool}' is required but not installed.\n")
                self.main_hub_tabs.setCurrentIndex(2) # Switch to Engine Center
                continue

            # Launch asynchronous metadata and thumbnail probe
            u_low = url.lower()
            if "youtube.com" in u_low or "youtu.be" in u_low or "spotify.com" in u_low:
                probe_worker = MetadataProbeWorker(download_id, url, target_tool, self)
                probe_worker.metadata_ready.connect(self.on_metadata_probed)
                probe_worker.start()
                self.probe_workers[download_id] = probe_worker

            job_info = {
                "download_id": download_id,
                "target_tool": target_tool,
                "target_path": target_path,
                "url": url,
                "export_dir": export_dir,
                "target_settings": target_settings,
                "progress_card": progress_card
            }

            self.job_registry[download_id] = job_info
            progress_card.set_queued()
            self.pending_queue.append(job_info)

        self.update_queue_counter()
        self.process_queue()

    def process_queue(self):
        while len(self.active_workers) < self.max_concurrent_downloads and self.pending_queue:
            job = self.pending_queue.pop(0)
            download_id = job["download_id"]
            progress_card = job["progress_card"]

            progress_card.set_running()
            if job["target_tool"] != self.config_manager.get_active_profile().get("tool"):
                self.on_download_log(download_id, f"[Nexus Ingest] Routing '{job['url']}' to specialized engine '{job['target_tool']}'.\n")

            worker = DownloadWorker(
                download_id, job["target_tool"], job["target_path"],
                job["url"], job["export_dir"], job["target_settings"]
            )
            worker.progress_updated.connect(self.on_download_progress)
            worker.download_completed.connect(self.on_download_completed)
            worker.log_received.connect(self.on_download_log)

            self.active_workers[download_id] = (worker, progress_card, job)
            worker.start()

        self.update_queue_counter()

    @pyqtSlot(str, int, str, str, str)
    def on_download_progress(self, download_id, percent, speed, eta, status):
        if download_id in self.active_workers:
            _, card, _ = self.active_workers[download_id]
            card.update_progress(percent, speed, eta, status)
            if speed and speed != "-":
                self.active_speeds[download_id] = speed
            self.update_aggregate_speed()

    @pyqtSlot(str, str, str, bytes)
    def on_metadata_probed(self, download_id, title, uploader, thumb_bytes):
        if download_id in self.job_registry:
            card = self.job_registry[download_id].get("progress_card")
            if card:
                card.set_media_metadata(title, uploader, thumb_bytes)
        if download_id in self.probe_workers:
            worker = self.probe_workers.pop(download_id)
            worker.deleteLater()

    @pyqtSlot(str, bool, str)
    def on_download_completed(self, download_id, success, error_msg):
        if download_id in self.active_workers:
            worker, card, job = self.active_workers[download_id]
            final_file = worker.get_final_file()

            if success:
                card.set_completed()
            else:
                card.set_error(error_msg)

            # Record in persistent history
            self.history_manager.add_record(
                download_id=download_id,
                url=job["url"],
                tool=job["target_tool"],
                status="completed" if success else "error",
                export_dir=job["export_dir"],
                file_path=final_file,
                error_msg=error_msg
            )
            self.load_history_table()

            worker.quit()
            worker.wait(1000)
            del self.active_workers[download_id]
            if download_id in self.active_speeds:
                del self.active_speeds[download_id]

            # Check if entire queue finished
            if len(self.active_workers) == 0 and len(self.pending_queue) == 0:
                self.notify_user("Ingest Complete", "All queued media downloads have finished!")

            self.update_queue_counter()
            self.process_queue()

    def retry_download(self, download_id):
        if download_id in self.job_registry:
            job = self.job_registry[download_id]
            card = job["progress_card"]
            card.set_queued()
            self.pending_queue.append(job)
            self.update_queue_counter()
            self.process_queue()

    @pyqtSlot(str, str)
    def on_download_log(self, download_id, log_line):
        self.logs_console.appendPlainText(log_line)
        if self.autoscroll_cb.isChecked():
            sb = self.logs_console.verticalScrollBar()
            sb.setValue(sb.maximum())

    @pyqtSlot(str)
    def cancel_download(self, download_id):
        if download_id in self.active_workers:
            worker, card, job = self.active_workers[download_id]
            self.zombie_workers.add(worker)
            worker.finished.connect(lambda w=worker: self.zombie_workers.discard(w))
            worker.cancel()
            if card:
                card.set_error("Cancelled by user")
            del self.active_workers[download_id]
            if download_id in self.active_speeds:
                del self.active_speeds[download_id]
            self.update_queue_counter()
            self.process_queue()
        else:
            for idx, job in enumerate(self.pending_queue):
                if job["download_id"] == download_id:
                    self.pending_queue.pop(idx)
                    card = job.get("progress_card")
                    if card:
                        card.set_error("Cancelled by user")
                    self.update_queue_counter()
                    break

    def cancel_all_downloads(self):
        for job in self.pending_queue:
            card = job.get("progress_card")
            if card:
                card.set_error("Cancelled by user")
        self.pending_queue.clear()

        for download_id, (worker, card, job) in list(self.active_workers.items()):
            self.zombie_workers.add(worker)
            worker.finished.connect(lambda w=worker: self.zombie_workers.discard(w))
            worker.cancel()
            if card:
                card.set_error("Cancelled by user")
        self.active_workers.clear()
        self.active_speeds.clear()
        self.update_queue_counter()

    def clear_completed_downloads(self):
        for i in reversed(range(self.queue_list_layout.count())):
            widget = self.queue_list_layout.itemAt(i).widget()
            if isinstance(widget, DownloadProgressWidget):
                btn_text = widget.action_btn.text()
                if btn_text in ["Clear", "Remove"]:
                    widget.setParent(None)
                    widget.deleteLater()

    def clear_logs(self):
        self.logs_console.clear()

    def copy_logs_to_clipboard(self):
        text = self.logs_console.toPlainText()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            CyberMessageBox.show_info(self, "Copied", "Console logs copied to clipboard!", border_color="#00f0ff")

    # ----------------- SYSTEM TRAY & NOTIFICATIONS -----------------
    def setup_system_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.windowIcon())
        tray_menu = QMenu()
        show_action = tray_menu.addAction("Show Nexus")
        show_action.triggered.connect(self.show_and_activate)
        tray_menu.addSeparator()
        cancel_action = tray_menu.addAction("Cancel All Downloads")
        cancel_action.triggered.connect(self.cancel_all_downloads)
        tray_menu.addSeparator()
        quit_action = tray_menu.addAction("Quit Nexus")
        quit_action.triggered.connect(self.force_quit)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

    def show_and_activate(self):
        self.showNormal()
        self.activateWindow()

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show_and_activate()

    def force_quit(self):
        self.cancel_all_downloads()
        QApplication.quit()

    def notify_user(self, title, message):
        if hasattr(self, 'tray_icon') and self.tray_icon and self.tray_icon.isVisible():
            self.tray_icon.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, 4000)

    def closeEvent(self, event):
        active_count = len(self.active_workers)
        queued_count = len(self.pending_queue)
        if active_count > 0 or queued_count > 0:
            reply = CyberMessageBox.show_question(
                self, "Active Ingest Jobs",
                f"There are {active_count} active downloads and {queued_count} queued jobs in progress.\n\nAre you sure you want to cancel everything and exit?"
            )
            if not reply:
                event.ignore()
                return

        for download_id, (worker, _, _) in list(self.active_workers.items()):
            worker.cancel()
            worker.quit()
            worker.wait()
        event.accept()
