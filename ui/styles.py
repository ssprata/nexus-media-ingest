"""Cyberpunk / Synthwave Neon Theme Stylesheet for Multi-Downloader Tool."""

CYBERPUNK_STYLE = """
/* Cyberpunk / Synthwave Studio QSS Stylesheet */

QMainWindow {
    background-color: #0c0d14;
    color: #f1f5f9;
}

QWidget {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Arial, sans-serif;
    color: #e2e8f0;
    font-size: 13px;
}

/* Scrollbars styling */
QScrollBar:vertical {
    border: none;
    background: #090a0f;
    width: 9px;
    margin: 0;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #7928ca;
    min-height: 25px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #00f0ff;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

QScrollBar:horizontal {
    border: none;
    background: #090a0f;
    height: 9px;
    margin: 0;
    border-radius: 4px;
}
QScrollBar::handle:horizontal {
    background: #7928ca;
    min-width: 25px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal:hover {
    background: #00f0ff;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: none;
}

/* Splitter */
QSplitter::handle {
    background-color: #1a1c2c;
}
QSplitter::handle:horizontal {
    width: 6px;
    margin: 0px 1px;
}
QSplitter::handle:vertical {
    height: 6px;
    margin: 1px 0px;
}
QSplitter::handle:hover {
    background-color: #00f0ff;
}
QSplitter::handle:pressed {
    background-color: #ff007f;
}

/* Sidebar & Cards */
QFrame#top_header_bar {
    background-color: #11121c;
    border-bottom: 2px solid #1e2030;
}

QFrame#sidebar_frame {
    background-color: #11121c;
    border-right: 1px solid #1e2030;
}

QFrame#card_frame {
    background-color: #131522;
    border: 1px solid #23263b;
    border-radius: 10px;
}
QFrame#card_frame:hover {
    border-color: #2e324e;
}

QFrame#progress_card {
    background-color: #141726;
    border: 1px solid #282c44;
    border-left: 4px solid #00f0ff;
    border-radius: 8px;
}
QFrame#progress_card[state="completed"] {
    border-left: 4px solid #10b981;
}
QFrame#progress_card[state="error"] {
    border-left: 4px solid #ef4444;
}

/* Labels */
QLabel {
    font-size: 13px;
}
QLabel#app_title {
    font-size: 18px;
    font-weight: 900;
    color: #00f0ff;
    letter-spacing: 1.5px;
}
QLabel#app_subtitle {
    font-size: 11px;
    font-weight: bold;
    color: #ff007f;
    letter-spacing: 1px;
}
QLabel#header_label {
    font-size: 14px;
    font-weight: bold;
    color: #00f0ff;
    letter-spacing: 0.5px;
}
QLabel#section_title {
    font-size: 12px;
    font-weight: 800;
    color: #9d4edd;
    letter-spacing: 1px;
    text-transform: uppercase;
}
QLabel#badge_online {
    background-color: rgba(16, 185, 129, 0.15);
    border: 1px solid #10b981;
    color: #10b981;
    border-radius: 12px;
    padding: 3px 8px;
    font-size: 11px;
    font-weight: bold;
}
QLabel#badge_offline {
    background-color: rgba(239, 68, 68, 0.15);
    border: 1px solid #ef4444;
    color: #ef4444;
    border-radius: 12px;
    padding: 3px 8px;
    font-size: 11px;
    font-weight: bold;
}

/* Inputs & Textareas */
QLineEdit {
    background-color: #161827;
    border: 1px solid #282c44;
    border-radius: 6px;
    padding: 7px 12px;
    color: #ffffff;
    font-size: 13px;
}
QLineEdit:focus {
    border: 1px solid #00f0ff;
    background-color: #1a1c2e;
}

QTextEdit, QPlainTextEdit {
    background-color: #161827;
    border: 1px solid #282c44;
    border-radius: 6px;
    padding: 8px 12px;
    color: #f1f5f9;
    font-family: 'Cascadia Code', 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    line-height: 1.4;
}
QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #00f0ff;
    background-color: #1a1c2e;
}

/* Dropdowns / ComboBoxes */
QComboBox {
    background-color: #161827;
    border: 1px solid #282c44;
    border-radius: 6px;
    padding: 6px 12px;
    color: #ffffff;
    font-size: 13px;
    min-width: 110px;
}
QComboBox:focus, QComboBox:hover {
    border: 1px solid #9d4edd;
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border-left-width: 0px;
    border-top-right-radius: 6px;
    border-bottom-right-radius: 6px;
}
QComboBox QAbstractItemView {
    background-color: #161827;
    border: 1px solid #282c44;
    selection-background-color: #7928ca;
    selection-color: #ffffff;
    color: #ffffff;
    padding: 4px;
}

/* Tree Widgets (Profiles tree list) */
QTreeWidget {
    background-color: #161827;
    border: 1px solid #282c44;
    border-radius: 8px;
    padding: 6px;
    color: #ffffff;
    font-size: 13px;
}
QTreeWidget::item {
    border-radius: 5px;
    padding: 6px 8px;
    margin: 2px 0;
}
QTreeWidget::item:hover {
    background-color: #21243a;
    color: #00f0ff;
}
QTreeWidget::item:selected {
    background-color: #7928ca;
    color: #ffffff;
    font-weight: bold;
}

/* Tab Widgets */
QTabWidget::pane {
    border: 1px solid #282c44;
    background-color: #131522;
    border-radius: 8px;
    top: -1px;
}
QTabBar::tab {
    background-color: #161827;
    border: 1px solid #282c44;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 16px;
    color: #94a3b8;
    font-size: 12px;
    font-weight: 700;
    margin-right: 4px;
}
QTabBar::tab:hover {
    color: #ffffff;
    background-color: #21243a;
}
QTabBar::tab:selected {
    background-color: #131522;
    border-color: #282c44;
    border-bottom: 2px solid #00f0ff;
    color: #00f0ff;
}

/* Bottom Dock Tabs */
QTabWidget#activity_tab_widget::pane {
    border: 1px solid #282c44;
    background-color: #111320;
    border-radius: 8px;
}
QTabWidget#activity_tab_widget QTabBar::tab:selected {
    background-color: #111320;
    border-bottom: 2px solid #ff007f;
    color: #ff007f;
}

/* Spinboxes & checkboxes */
QSpinBox {
    background-color: #161827;
    border: 1px solid #282c44;
    border-radius: 6px;
    padding: 6px 10px;
    color: #ffffff;
}
QSpinBox:focus {
    border: 1px solid #00f0ff;
}

QCheckBox {
    spacing: 8px;
    font-size: 13px;
    color: #e2e8f0;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #282c44;
    border-radius: 4px;
    background-color: #161827;
}
QCheckBox::indicator:unchecked:hover {
    border: 1px solid #00f0ff;
}
QCheckBox::indicator:checked {
    border: 1px solid #00f0ff;
    background-color: #00f0ff;
}

/* Progress Bar */
QProgressBar {
    background-color: #181b2c;
    border: 1px solid #282c44;
    border-radius: 5px;
    text-align: center;
    color: #ffffff;
    font-size: 11px;
    font-weight: bold;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #7928ca, stop:0.5 #ff007f, stop:1 #00f0ff);
    border-radius: 4px;
}

/* Buttons */
QPushButton {
    background-color: #1a1d2e;
    border: 1px solid #282c44;
    border-radius: 6px;
    color: #ffffff;
    padding: 7px 14px;
    font-weight: 600;
    font-size: 12px;
}
QPushButton:hover {
    background-color: #252940;
    border-color: #00f0ff;
}
QPushButton:pressed {
    background-color: #0f111c;
}
QPushButton:disabled {
    background-color: #141622;
    border-color: #202334;
    color: #4b5563;
}

/* Glowing Neon buttons */
QPushButton#neon_magenta_btn {
    border: 1px solid #ff007f;
    color: #ffffff;
    background-color: rgba(255, 0, 127, 0.12);
}
QPushButton#neon_magenta_btn:hover {
    background-color: #ff007f;
    color: #ffffff;
}

QPushButton#neon_cyan_btn {
    border: 1px solid #00f0ff;
    color: #00f0ff;
    background-color: rgba(0, 240, 255, 0.1);
}
QPushButton#neon_cyan_btn:hover {
    background-color: #00f0ff;
    color: #0c0d14;
    font-weight: bold;
}

QPushButton#neon_purple_btn {
    border: 1px solid #9d4edd;
    color: #c77dff;
    background-color: rgba(157, 78, 221, 0.12);
}
QPushButton#neon_purple_btn:hover {
    background-color: #9d4edd;
    color: #ffffff;
}

QPushButton#download_btn {
    border: 2px solid #00f0ff;
    color: #ffffff;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 rgba(121, 40, 202, 0.4), stop:1 rgba(0, 240, 255, 0.4));
    font-size: 15px;
    font-weight: 800;
    border-radius: 8px;
    padding: 11px 22px;
    letter-spacing: 1px;
}
QPushButton#download_btn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #7928ca, stop:1 #00f0ff);
    color: #0c0d14;
    border-color: #00f0ff;
}
QPushButton#download_btn:disabled {
    border-color: #282c44;
    background: #161827;
    color: #64748b;
}

/* Console logs */
QPlainTextEdit#logs_console {
    background-color: #0a0b12;
    border: 1px solid #202336;
    border-radius: 6px;
    color: #38bdf8;
    font-family: 'Cascadia Code', 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    line-height: 1.4;
}

/* GroupBox */
QGroupBox {
    border: 1px solid #282c44;
    border-radius: 8px;
    margin-top: 10px;
    padding-top: 12px;
    font-weight: bold;
    color: #9d4edd;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 5px;
}
"""
