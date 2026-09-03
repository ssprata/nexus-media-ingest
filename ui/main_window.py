import os
import subprocess
import uuid
from PyQt6.QtCore import Qt, pyqtSignal, QThread, pyqtSlot, QTimer
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPlainTextEdit, QPushButton, QListWidget,
    QComboBox, QProgressBar, QTabWidget, QSpinBox, QCheckBox,
    QFileDialog, QMessageBox, QSplitter, QScrollArea, QFrame,
    QSizePolicy, QFormLayout, QGroupBox, QDialog, QTreeWidget, QTreeWidgetItem,
    QApplication
)
from PyQt6.QtGui import QColor, QFont, QClipboard

from config_manager import ConfigManager
from dependency_manager import DependencyManager
from downloader import DownloadWorker


class CyberMessageBox(QDialog):
    def __init__(self, title, message, is_confirm=False, border_color="#ff007f", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        
        self.setObjectName("card_frame")
        self.setStyleSheet(f"""
            QDialog#card_frame {{
                background-color: #121420;
                border: 2px solid {border_color};
                border-radius: 10px;
            }}
        """)
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
                background-color: #121420;
                border: 2px solid #00f0ff;
                border-radius: 10px;
            }
        """)
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
class CookieManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("YouTube Cookie & Bot-Bypass Manager")
        self.setMinimumWidth(560)
        self.setMinimumHeight(440)
        self.setObjectName("card_frame")
        self.setStyleSheet("""
            QDialog#card_frame {
                background-color: #121420;
                border: 2px solid #00f0ff;
                border-radius: 10px;
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



class DownloadProgressWidget(QFrame):
    cancelled = pyqtSignal(str)

    def __init__(self, download_id, url, target_dir="", parent=None):
        super().__init__(parent)
        self.download_id = download_id
        self.url = url
        self.target_dir = target_dir
        self.setObjectName("progress_card")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        # Header Row: URL & Actions
        top_row = QHBoxLayout()
        display_url = self.url
        if len(display_url) > 75:
            display_url = display_url[:72] + "..."
        
        self.url_label = QLabel(display_url)
        self.url_label.setStyleSheet("font-weight: bold; color: #00f0ff; font-size: 13px;")
        
        self.open_dir_btn = QPushButton("📂 Open Folder")
        self.open_dir_btn.setObjectName("neon_cyan_btn")
        self.open_dir_btn.setFixedHeight(26)
        self.open_dir_btn.setVisible(False)
        self.open_dir_btn.clicked.connect(self.on_open_folder_clicked)

        self.action_btn = QPushButton("Cancel")
        self.action_btn.setObjectName("neon_magenta_btn")
        self.action_btn.setFixedWidth(75)
        self.action_btn.setFixedHeight(26)
        self.action_btn.clicked.connect(self.on_action_clicked)

        top_row.addWidget(self.url_label)
        top_row.addStretch()
        top_row.addWidget(self.open_dir_btn)
        top_row.addWidget(self.action_btn)
        layout.addLayout(top_row)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(10)
        layout.addWidget(self.progress_bar)

        # Status row
        status_row = QHBoxLayout()
        self.status_label = QLabel("Initializing download...")
        self.status_label.setStyleSheet("color: #94a3b8; font-size: 12px;")
        
        self.metrics_label = QLabel("- | ETA: -")
        self.metrics_label.setStyleSheet("color: #ff007f; font-weight: bold; font-size: 12px;")

        status_row.addWidget(self.status_label)
        status_row.addStretch()
        status_row.addWidget(self.metrics_label)
        layout.addLayout(status_row)

    def update_progress(self, percent, speed, eta, status):
        if percent >= 0:
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(100)
            self.progress_bar.setValue(percent)
            if percent == 100:
                self.progress_bar.setFormat("100% (Completed)")
        else:
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(0)
            self.progress_bar.setFormat("")
        
        self.status_label.setText(status)
        if speed == "-" and eta == "-":
            self.metrics_label.setText("")
        else:
            self.metrics_label.setText(f"⚡ {speed}  ⏱ ETA {eta}")

    def set_error(self, error_msg):
        self.setProperty("state", "error")
        self.style().unpolish(self)
        self.style().polish(self)

        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #ef4444; }")
        self.status_label.setText(f"❌ Error: {error_msg}")
        self.status_label.setStyleSheet("color: #ef4444; font-weight: bold;")
        self.metrics_label.setText("")
        
        self.action_btn.setText("Clear")
        self.action_btn.setObjectName("neon_magenta_btn")
        self.action_btn.clicked.disconnect()
        self.action_btn.clicked.connect(self.on_remove_clicked)

    def set_completed(self):
        self.setProperty("state", "completed")
        self.style().unpolish(self)
        self.style().polish(self)

        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(100)
        self.status_label.setText("✔ Download completed successfully")
        self.status_label.setStyleSheet("color: #10b981; font-weight: bold;")
        self.metrics_label.setText("")
        
        if self.target_dir and os.path.exists(self.target_dir):
            self.open_dir_btn.setVisible(True)

        self.action_btn.setText("Clear")
        self.action_btn.setObjectName("neon_cyan_btn")
        self.action_btn.clicked.disconnect()
        self.action_btn.clicked.connect(self.on_remove_clicked)

    def on_action_clicked(self):
        self.cancelled.emit(self.download_id)

    def on_remove_clicked(self):
        self.setParent(None)
        self.deleteLater()

    def on_open_folder_clicked(self):
        if self.target_dir and os.path.exists(self.target_dir):
            os.startfile(self.target_dir)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cyberpunk Multi-Downloader Studio")
        self.resize(1180, 820)
        self.setMinimumSize(980, 680)

        # Managers
        self.config_manager = ConfigManager()
        self.dep_manager = DependencyManager()

        # Trackers
        self.active_workers = {}
        self.tool_download_workers = {}
        self.batch_update_worker = None
        self.engine_badges = {}
        self.expanded_folders = set()
        self.is_loading_profile = False

        # Build UI
        self.setup_ui()
        self.load_profiles()
        self.refresh_tools_status()

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
        app_title = QLabel("⚡ MULTI-DOWNLOADER STUDIO")
        app_title.setObjectName("app_title")
        app_subtitle = QLabel("CYBERPUNK HIGH-PERFORMANCE SUITE")
        app_subtitle.setObjectName("app_subtitle")
        brand_layout.addWidget(app_title)
        brand_layout.addWidget(app_subtitle)
        header_layout.addLayout(brand_layout)

        header_layout.addSpacing(16)

        # Live Engine Badges in Header
        self.engine_badges_layout = QHBoxLayout()
        self.engine_badges_layout.setSpacing(8)
        for t in ["yt-dlp", "aria2c", "ffmpeg", "spotdl", "gallery-dl", "instagram"]:
            badge = QLabel(f"{t}: Checking...")
            badge.setObjectName("badge_offline")
            self.engine_badges_layout.addWidget(badge)
            self.engine_badges[t] = badge
        header_layout.addLayout(self.engine_badges_layout)

        header_layout.addStretch()

        # Quick Actions in Header
        self.cookie_manager_btn = QPushButton("🍪 Cookie Manager")
        self.cookie_manager_btn.setObjectName("neon_yellow_btn")
        self.cookie_manager_btn.clicked.connect(self.on_open_cookie_manager)
        header_layout.addWidget(self.cookie_manager_btn)

        self.quick_update_btn = QPushButton("⚡ Update Engines")
        self.quick_update_btn.setObjectName("neon_purple_btn")
        self.quick_update_btn.clicked.connect(self.update_all_engines)
        header_layout.addWidget(self.quick_update_btn)

        self.open_active_dir_btn = QPushButton("📂 Open Download Dir")
        self.open_active_dir_btn.setObjectName("neon_cyan_btn")
        self.open_active_dir_btn.clicked.connect(self.on_open_current_export_dir)
        header_layout.addWidget(self.open_active_dir_btn)

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

        # Profiles Tree List
        self.profiles_list = ProfileTreeWidget()
        self.profiles_list.setHeaderHidden(True)
        self.profiles_list.itemClicked.connect(self.on_profile_item_clicked)
        self.profiles_list.profile_moved.connect(self.on_profile_moved)
        self.profiles_list.itemExpanded.connect(self.on_folder_expanded)
        self.profiles_list.itemCollapsed.connect(self.on_folder_collapsed)
        sidebar_layout.addWidget(self.profiles_list, 1)

        # Profile Buttons Row
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

        # Profile Quick Config Card
        self.profile_details_frame = QFrame()
        self.profile_details_frame.setObjectName("card_frame")
        details_layout = QVBoxLayout(self.profile_details_frame)
        details_layout.setContentsMargins(12, 12, 12, 12)
        details_layout.setSpacing(8)

        card_title = QLabel("ACTIVE PROFILE SETTINGS")
        card_title.setObjectName("section_title")
        details_layout.addWidget(card_title)

        form_layout = QFormLayout()
        form_layout.setSpacing(8)

        self.prof_name_input = QLineEdit()
        form_layout.addRow("Name:", self.prof_name_input)

        self.prof_folder_input = QComboBox()
        self.prof_folder_input.setEditable(True)
        form_layout.addRow("Folder:", self.prof_folder_input)

        self.prof_tool_combo = QComboBox()
        self.prof_tool_combo.addItems(["yt-dlp", "aria2c", "gallery-dl", "spotdl", "instagram"])
        self.prof_tool_combo.currentTextChanged.connect(self.on_tool_combo_changed)
        form_layout.addRow("Engine:", self.prof_tool_combo)

        # Directory Selector
        dir_layout = QHBoxLayout()
        self.prof_dir_input = QLineEdit()
        self.prof_dir_btn = QPushButton("Browse")
        self.prof_dir_btn.setFixedWidth(65)
        self.prof_dir_btn.clicked.connect(self.on_browse_directory)
        dir_layout.addWidget(self.prof_dir_input)
        dir_layout.addWidget(self.prof_dir_btn)
        form_layout.addRow("Export:", dir_layout)

        details_layout.addLayout(form_layout)

        self.save_profile_btn = QPushButton("💾 Save Profile")
        self.save_profile_btn.setObjectName("neon_cyan_btn")
        self.save_profile_btn.clicked.connect(self.on_save_profile_settings)
        details_layout.addWidget(self.save_profile_btn)

        sidebar_layout.addWidget(self.profile_details_frame)
        main_splitter.addWidget(sidebar)

        # ----------------- RIGHT WORKSPACE AREA -----------------
        workspace = QWidget()
        workspace_layout = QVBoxLayout(workspace)
        workspace_layout.setContentsMargins(14, 14, 14, 14)
        workspace_layout.setSpacing(12)

        # --- Top Command Center: URL Batch Input ---
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
        self.urls_input.setMaximumHeight(110)
        input_card_layout.addWidget(self.urls_input)

        # Start Download Button
        self.download_btn = QPushButton("⚡ ENGAGE DOWNLOAD BATCH")
        self.download_btn.setObjectName("download_btn")
        self.download_btn.clicked.connect(self.start_download_batch)
        input_card_layout.addWidget(self.download_btn)

        workspace_layout.addWidget(input_card)

        # --- Main Tabbed Hub: Queue, Engine Settings, Logs & Manager ---
        self.main_hub_tabs = QTabWidget()
        self.main_hub_tabs.setObjectName("activity_tab_widget")

        # TAB 1: 📥 Active Queue
        queue_tab = QWidget()
        queue_tab_layout = QVBoxLayout(queue_tab)
        queue_tab_layout.setContentsMargins(10, 10, 10, 10)
        queue_tab_layout.setSpacing(8)

        queue_control_row = QHBoxLayout()
        self.queue_count_lbl = QLabel("Queue: 0 items active")
        self.queue_count_lbl.setStyleSheet("color: #00f0ff; font-weight: bold;")
        queue_control_row.addWidget(self.queue_count_lbl)

        queue_control_row.addStretch()

        self.clear_completed_btn = QPushButton("🧹 Clear Completed")
        self.clear_completed_btn.clicked.connect(self.clear_completed_downloads)
        queue_control_row.addWidget(self.clear_completed_btn)

        self.cancel_all_btn = QPushButton("🛑 Cancel All")
        self.cancel_all_btn.setObjectName("neon_magenta_btn")
        self.cancel_all_btn.clicked.connect(self.cancel_all_downloads)
        queue_control_row.addWidget(self.cancel_all_btn)

        queue_tab_layout.addLayout(queue_control_row)

        self.queue_scroll = QScrollArea()
        self.queue_scroll.setWidgetResizable(True)
        self.queue_scroll_content = QWidget()
        self.queue_list_layout = QVBoxLayout(self.queue_scroll_content)
        self.queue_list_layout.setContentsMargins(4, 4, 4, 4)
        self.queue_list_layout.setSpacing(8)
        self.queue_list_layout.addStretch()
        self.queue_scroll.setWidget(self.queue_scroll_content)
        queue_tab_layout.addWidget(self.queue_scroll)

        self.main_hub_tabs.addTab(queue_tab, "📥 Active Queue (0)")

        # TAB 2: ⚙️ Engine Settings (All 5 engines in dedicated sub-tabs)
        settings_tab = QWidget()
        settings_tab_layout = QVBoxLayout(settings_tab)
        settings_tab_layout.setContentsMargins(10, 10, 10, 10)
        settings_tab_layout.setSpacing(8)

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
        self.spotdl_audio_q.addItems(["best", "320k", "256k", "192k", "128k"])
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

        settings_tab_layout.addWidget(self.config_tabs)
        self.main_hub_tabs.addTab(settings_tab, "⚙️ Engine Settings")

        # TAB 3: 📜 Console Logs
        logs_tab = QWidget()
        logs_tab_layout = QVBoxLayout(logs_tab)
        logs_tab_layout.setContentsMargins(10, 10, 10, 10)
        logs_tab_layout.setSpacing(8)

        logs_control_row = QHBoxLayout()
        logs_lbl = QLabel("ENGINE REAL-TIME OUTPUT STREAM")
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
        self.logs_console.setPlaceholderText("Subprocess standard outputs and telemetry will stream here...")
        logs_tab_layout.addWidget(self.logs_console)

        self.main_hub_tabs.addTab(logs_tab, "📜 Console Logs")

        # TAB 4: 🛠 Engine Manager
        engines_tab = QWidget()
        engines_tab_layout = QVBoxLayout(engines_tab)
        engines_tab_layout.setContentsMargins(14, 12, 14, 12)
        engines_tab_layout.setSpacing(10)

        engines_header_row = QHBoxLayout()
        engines_title = QLabel("ENGINE BINARIES & STATUS DASHBOARD")
        engines_title.setStyleSheet("color: #9d4edd; font-weight: bold; font-size: 13px;")
        engines_header_row.addWidget(engines_title)
        engines_header_row.addStretch()

        refresh_engines_btn = QPushButton("🔄 Refresh Status")
        refresh_engines_btn.clicked.connect(self.refresh_tools_status)
        engines_header_row.addWidget(refresh_engines_btn)

        self.update_all_tab_btn = QPushButton("⚡ Update All Engines")
        self.update_all_tab_btn.setObjectName("neon_cyan_btn")
        self.update_all_tab_btn.clicked.connect(self.update_all_engines)
        engines_header_row.addWidget(self.update_all_tab_btn)

        engines_tab_layout.addLayout(engines_header_row)

        self.engine_widgets = {}
        tools_list = [
            ("yt-dlp", "YouTube, Twitch, Twitter, Vimeo video engine"),
            ("aria2c", "Multi-connection high-speed direct downloader"),
            ("ffmpeg", "Video muxing, H.264/AAC converter & audio extractor"),
            ("spotdl", "Spotify track & playlist downloader"),
            ("gallery-dl", "Image gallery & multi-post downloader"),
            ("instagram", "Instagram media extractor (Instaloader)")
        ]

        for tool, desc in tools_list:
            card = QFrame()
            card.setObjectName("card_frame")
            card_l = QHBoxLayout(card)
            card_l.setContentsMargins(12, 8, 12, 8)
            card_l.setSpacing(12)

            t_lbl = QLabel(f"<b>{tool}</b>")
            t_lbl.setStyleSheet("font-size: 13px; color: #ffffff;")
            t_lbl.setFixedWidth(80)

            d_lbl = QLabel(desc)
            d_lbl.setStyleSheet("color: #94a3b8; font-size: 12px;")

            v_lbl = QLabel("Checking...")
            v_lbl.setStyleSheet("color: #00f0ff; font-weight: bold; font-size: 12px;")
            v_lbl.setFixedWidth(130)

            btn = QPushButton("Update / Install")
            btn.setObjectName("neon_cyan_btn")
            btn.setFixedWidth(130)
            btn.clicked.connect(lambda checked, t=tool: self.download_binary(t, is_update=self.dep_manager.is_installed(t)))

            card_l.addWidget(t_lbl)
            card_l.addWidget(d_lbl, 1)
            card_l.addWidget(v_lbl)
            card_l.addWidget(btn)

            self.engine_widgets[tool] = {"version_lbl": v_lbl, "btn": btn}
            engines_tab_layout.addWidget(card)

        # Tool download progress bar in Engine Tab
        self.tool_progress_lbl = QLabel("")
        self.tool_progress_lbl.setStyleSheet("color: #00f0ff; font-weight: bold;")
        self.tool_progress_bar = QProgressBar()
        self.tool_progress_bar.setVisible(False)
        engines_tab_layout.addWidget(self.tool_progress_lbl)
        engines_tab_layout.addWidget(self.tool_progress_bar)

        engines_tab_layout.addStretch()
        self.main_hub_tabs.addTab(engines_tab, "🛠 Engine Manager")

        workspace_layout.addWidget(self.main_hub_tabs, 1)
        main_splitter.addWidget(workspace)
        main_splitter.setSizes([310, 870])

        # Connect auto-save signals for tab inputs
        self.connect_auto_save_signals()
        self.update_cookie_header_badge()

    def update_queue_counter(self):
        active_count = len(self.active_workers)
        self.queue_count_lbl.setText(f"Queue: {active_count} active downloads")
        self.main_hub_tabs.setTabText(0, f"📥 Active Queue ({active_count})")

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
        ytdlp_settings = {
            "format": fmt,
            "video_format": self.ytdlp_video_fmt.currentText(),
            "extract_audio": self.ytdlp_audio_cb.isChecked(),
            "audio_format": self.ytdlp_audio_fmt.currentText(),
            "audio_quality": str(self.ytdlp_audio_q.value()),
            "embed_subs": self.ytdlp_subs_cb.isChecked(),
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
        self.prof_dir_input.setText(active_prof["export_dir"])

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
            self.spotdl_audio_q.setCurrentText(sdl_s.get("audio_quality", "best"))
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
            "export_dir": os.path.expanduser("~/Downloads"),
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
            "spotdl_settings": {"audio_format": "mp3", "audio_quality": "best", "custom_flags": ""},
            "instagram_settings": {"download_pictures": True, "download_videos": True, "download_metadata": False, "download_comments": False, "output_type": "video_mp4", "custom_flags": ""}
        }
        
        self.config_manager.add_profile(new_profile)
        self.config_manager.set_active_profile(profile_name)
        self.expanded_folders.add(folder_name)
        self.load_profiles()

    def on_add_profile(self):
        default_folder = ""
        curr_item = self.profiles_list.currentItem()
        if curr_item:
            role = curr_item.data(0, Qt.ItemDataRole.UserRole)
            if role == "folder":
                default_folder = curr_item.data(0, Qt.ItemDataRole.UserRole + 1)
            elif role == "profile":
                parent = curr_item.parent()
                if parent:
                    default_folder = parent.data(0, Qt.ItemDataRole.UserRole + 1)

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
            "export_dir": os.path.expanduser("~/Downloads"),
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
            "spotdl_settings": {"audio_format": "mp3", "audio_quality": "best", "custom_flags": ""},
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
            self.cookie_manager_btn.setText(f"🍪 Cookies Active ({count})")
            self.cookie_manager_btn.setStyleSheet("""
                background-color: #064e3b;
                color: #34d399;
                border: 1px solid #10b981;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
            """)
        else:
            self.cookie_manager_btn.setText("🍪 Cookie Manager")
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
            current_dir = os.path.expanduser("~")
            
        selected_dir = QFileDialog.getExistingDirectory(
            self, "Select Download Destination Folder", current_dir
        )
        if selected_dir:
            self.prof_dir_input.setText(selected_dir.replace("/", "\\"))

    def on_open_current_export_dir(self):
        active_prof = self.config_manager.get_active_profile()
        if active_prof:
            path = active_prof.get("export_dir", "")
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
        export_dir = self.prof_dir_input.text().strip()

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
            "export_dir": export_dir,
            "aria2_settings": aria_settings,
            "ytdlp_settings": ytdlp_settings,
            "gallerydl_settings": gallerydl_settings,
            "spotdl_settings": spotdl_settings,
            "instagram_settings": instagram_settings
        }

        self.config_manager.update_profile(active_name, updated_profile)
        self.load_profiles()
        CyberMessageBox.show_info(self, "Settings Saved", f"Profile '{new_name}' saved successfully.", border_color="#00f0ff")

    # ----------------- TOOL DOWNLOADER & STATUS -----------------
    # ----------------- TOOL DOWNLOADER & STATUS -----------------
    def refresh_tools_status(self):
        tools = ["yt-dlp", "aria2c", "ffmpeg", "spotdl", "gallery-dl", "instagram"]

        for t in tools:
            is_ins = self.dep_manager.is_installed(t)
            version = self.dep_manager.get_tool_version(t) if is_ins else None

            if t in self.engine_widgets:
                w_info = self.engine_widgets[t]
                if is_ins:
                    v_str = f"v{version}" if version and not version.startswith("v") else (version or "Installed")
                    w_info["version_lbl"].setText(f"✔ {v_str}")
                    w_info["version_lbl"].setStyleSheet("color: #10b981; font-weight: bold; font-size: 12px;")
                    w_info["btn"].setText("Update")
                else:
                    w_info["version_lbl"].setText("❌ Missing")
                    w_info["version_lbl"].setStyleSheet("color: #ef4444; font-weight: bold; font-size: 12px;")
                    w_info["btn"].setText("Download & Install")

            if t in self.engine_badges:
                badge = self.engine_badges[t]
                badge.setText(f"{t}: {version[:12] if version else 'Missing'}")
                badge.setObjectName("badge_online" if is_ins else "badge_offline")
                badge.style().unpolish(badge)
                badge.style().polish(badge)

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
        if tool_name in self.engine_badges:
            badge = self.engine_badges[tool_name]
            badge.setText(f"{tool_name}: {version[:12] if version else 'Missing'}")
            badge.setObjectName("badge_online" if is_ins else "badge_offline")
            badge.style().unpolish(badge)
            badge.style().polish(badge)
        if tool_name in self.engine_widgets:
            w_info = self.engine_widgets[tool_name]
            if is_ins:
                v_str = f"v{version}" if version and not version.startswith("v") else (version or "Installed")
                w_info["version_lbl"].setText(f"✔ {v_str}")
                w_info["version_lbl"].setStyleSheet("color: #10b981; font-weight: bold; font-size: 12px;")

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
        export_dir = active_prof["export_dir"]

        # Switch to Queue tab immediately
        self.main_hub_tabs.setCurrentIndex(0)

        for url in urls:
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
                
            if not target_path:
                progress_card = DownloadProgressWidget(download_id, url, target_dir=export_dir)
                progress_card.cancelled.connect(self.cancel_download)
                self.queue_list_layout.insertWidget(0, progress_card)
                progress_card.set_error(f"Missing engine: '{target_tool}'")
                
                self.on_download_log(download_id, f"[ERROR] The engine '{target_tool}' is required but not installed.\n")
                self.main_hub_tabs.setCurrentIndex(3) # Switch to Engine manager
                continue

            progress_card = DownloadProgressWidget(download_id, url, target_dir=export_dir)
            progress_card.cancelled.connect(self.cancel_download)
            self.queue_list_layout.insertWidget(0, progress_card)

            if target_tool != tool_name:
                self.on_download_log(download_id, f"[INFO] URL matched specialized service. Automatically routing to '{target_tool}'.\n")

            worker = DownloadWorker(download_id, target_tool, target_path, url, export_dir, target_settings)
            worker.progress_updated.connect(self.on_download_progress)
            worker.download_completed.connect(self.on_download_completed)
            worker.log_received.connect(self.on_download_log)
            
            self.active_workers[download_id] = (worker, progress_card)
            worker.start()

        self.update_queue_counter()

    @pyqtSlot(str, int, str, str, str)
    def on_download_progress(self, download_id, percent, speed, eta, status):
        if download_id in self.active_workers:
            _, card = self.active_workers[download_id]
            card.update_progress(percent, speed, eta, status)

    @pyqtSlot(str, bool, str)
    def on_download_completed(self, download_id, success, error_msg):
        if download_id in self.active_workers:
            worker, card = self.active_workers[download_id]
            if success:
                card.set_completed()
            else:
                card.set_error(error_msg)
            
            worker.quit()
            worker.wait()
            del self.active_workers[download_id]
            self.update_queue_counter()

    @pyqtSlot(str, str)
    def on_download_log(self, download_id, log_line):
        self.logs_console.appendPlainText(log_line)
        if self.autoscroll_cb.isChecked():
            sb = self.logs_console.verticalScrollBar()
            sb.setValue(sb.maximum())

    @pyqtSlot(str)
    def cancel_download(self, download_id):
        if download_id in self.active_workers:
            worker, card = self.active_workers[download_id]
            worker.cancel()
            card.set_error("Cancelled by user")
            del self.active_workers[download_id]
            self.update_queue_counter()

    def cancel_all_downloads(self):
        for download_id, (worker, card) in list(self.active_workers.items()):
            worker.cancel()
            card.set_error("Cancelled by user")
        self.active_workers.clear()
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

    def closeEvent(self, event):
        for download_id, (worker, _) in list(self.active_workers.items()):
            worker.cancel()
            worker.quit()
            worker.wait()
        event.accept()
