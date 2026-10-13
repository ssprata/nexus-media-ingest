"""Nexus — High-Speed Media Ingest
Sleek OLED Pure Black & Cyber Neon Theme Stylesheet (QSS)
"""

CYBERPUNK_STYLE = """
/* ============================================================
   NEXUS OLED HIGH-CONTRAST NEON THEME
   ============================================================ */

QMainWindow {
    background-color: #000000;
    color: #f8fafc;
}

QWidget {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Arial, sans-serif;
    color: #e2e8f0;
    font-size: 10pt;
    selection-background-color: #7928ca;
    selection-color: #ffffff;
}

/* --- Scrollbars --- */
QScrollBar:vertical {
    border: none;
    background: #000000;
    width: 7px;
    margin: 0;
    border-radius: 3px;
}
QScrollBar::handle:vertical {
    background: #1e2238;
    min-height: 25px;
    border-radius: 3px;
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
    background: #000000;
    height: 7px;
    margin: 0;
    border-radius: 3px;
}
QScrollBar::handle:horizontal {
    background: #1e2238;
    min-width: 25px;
    border-radius: 3px;
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

/* --- Splitters --- */
QSplitter::handle {
    background-color: #0d0f18;
}
QSplitter::handle:horizontal {
    width: 4px;
}
QSplitter::handle:vertical {
    height: 4px;
}
QSplitter::handle:hover {
    background-color: #00f0ff;
}

/* --- Structural Frames & Cards --- */
QFrame#top_header_bar {
    background-color: #040508;
    border-bottom: 1px solid #141726;
}

QFrame#sidebar_frame {
    background-color: #040508;
    border-right: 1px solid #141726;
}

QFrame#card_frame {
    background-color: #080910;
    border: 1px solid #181c2e;
    border-radius: 10px;
}
QFrame#card_frame:hover {
    border-color: #262c47;
}

QFrame#armed_banner {
    background-color: #070a18;
    border: 1px solid #142038;
    border-left: 4px solid #00f0ff;
    border-radius: 8px;
}
QFrame#armed_banner:hover {
    border-color: #00f0ff;
    border-left: 4px solid #00f0ff;
    background-color: #0c1228;
}

QFrame#snapshot_card {
    background-color: #060712;
    border: 1px solid #1a2038;
    border-left: 4px solid #7928ca;
    border-radius: 8px;
}
QFrame#snapshot_card:hover {
    border-color: #a855f7;
    border-left: 4px solid #00f0ff;
    background-color: #0a0d20;
}

/* --- Progress Cards (Queue Items) --- */
QFrame#progress_card {
    background-color: #06070e;
    border: 1px solid #1a1e32;
    border-left: 4px solid #00f0ff;
    border-radius: 8px;
}
QFrame#progress_card:hover {
    border-color: #2b3252;
}
QFrame#progress_card[state="completed"] {
    border-left: 4px solid #00ff88;
}
QFrame#progress_card[state="error"] {
    border-left: 4px solid #ff0055;
}
QFrame#progress_card[state="queued"] {
    border-left: 4px solid #f59e0b;
}
QFrame#progress_card[state="running"] {
    border-left: 4px solid #00f0ff;
}

/* --- Typography & Badges --- */
QLabel {
    font-size: 13px;
    color: #cbd5e1;
}

QLabel#app_title {
    font-size: 19px;
    font-weight: 900;
    color: #ffffff;
    letter-spacing: 2px;
}

QLabel#app_subtitle {
    font-size: 10px;
    font-weight: 800;
    color: #ff007f;
    letter-spacing: 1.8px;
}

QLabel#header_label {
    font-size: 13px;
    font-weight: 800;
    color: #00f0ff;
    letter-spacing: 1px;
}

QLabel#section_title {
    font-size: 11px;
    font-weight: 800;
    color: #a855f7;
    letter-spacing: 1.2px;
}

/* Status Badges */
QLabel#badge_online, QLabel#badge_working {
    background-color: rgba(0, 255, 136, 0.08);
    border: 1px solid rgba(0, 255, 136, 0.4);
    color: #00ff88;
    border-radius: 11px;
    padding: 3px 9px;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 0.3px;
}

QLabel#badge_warning {
    background-color: rgba(251, 191, 36, 0.08);
    border: 1px solid rgba(251, 191, 36, 0.4);
    color: #fbbf24;
    border-radius: 11px;
    padding: 3px 9px;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 0.3px;
}

QLabel#badge_outdated {
    background-color: rgba(192, 132, 252, 0.08);
    border: 1px solid rgba(192, 132, 252, 0.4);
    color: #c084fc;
    border-radius: 11px;
    padding: 3px 9px;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 0.3px;
}

QLabel#badge_offline {
    background-color: rgba(255, 0, 85, 0.08);
    border: 1px solid rgba(255, 0, 85, 0.35);
    color: #ff0055;
    border-radius: 11px;
    padding: 3px 9px;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 0.3px;
}

/* Compact Top Header Engine Pills */
QPushButton#engine_top_pill {
    background-color: #060810;
    border: 1px solid #161b2e;
    border-radius: 12px;
    padding: 2px 10px;
    font-size: 11px;
    font-weight: 700;
    color: #94a3b8;
    min-height: 24px;
    max-height: 24px;
}
QPushButton#engine_top_pill:hover {
    background-color: #0e1222;
    border-color: #00f0ff;
    color: #ffffff;
}
QPushButton#engine_top_pill[status="working"] {
    border-color: rgba(0, 255, 136, 0.4);
    color: #00ff88;
    background-color: rgba(0, 255, 136, 0.06);
}
QPushButton#engine_top_pill[status="warning"] {
    border-color: rgba(251, 191, 36, 0.4);
    color: #fbbf24;
    background-color: rgba(251, 191, 36, 0.06);
}
QPushButton#engine_top_pill[status="outdated"] {
    border-color: rgba(192, 132, 252, 0.4);
    color: #c084fc;
    background-color: rgba(192, 132, 252, 0.06);
}
QPushButton#engine_top_pill[status="offline"] {
    border-color: rgba(255, 0, 85, 0.35);
    color: #ff0055;
    background-color: rgba(255, 0, 85, 0.06);
}

/* Interactive Engine Card */
QFrame#engine_card {
    background-color: #070812;
    border: 1px solid #181d32;
    border-radius: 10px;
    padding: 8px 10px;
}
QFrame#engine_card:hover {
    border-color: #00f0ff;
    background-color: #0c1022;
}

/* Clipboard Toast / Banner */
QFrame#clipboard_banner {
    background-color: #060914;
    border: 1px solid #00f0ff;
    border-radius: 8px;
    padding: 8px 14px;
}

/* Metric / HUD Pill */
QLabel#hud_metric_pill {
    background-color: rgba(0, 240, 255, 0.08);
    border: 1px solid rgba(0, 240, 255, 0.35);
    color: #00f0ff;
    border-radius: 7px;
    padding: 3px 9px;
    font-size: 11px;
    font-weight: 700;
    font-family: 'JetBrains Mono', Consolas, monospace;
}

/* --- Inputs & Fields --- */
QLineEdit {
    background-color: #0a0c16;
    border: 1px solid #1a1e32;
    border-radius: 7px;
    padding: 7px 12px;
    color: #ffffff;
    font-size: 13px;
}
QLineEdit:hover {
    border-color: #2a3150;
}
QLineEdit:focus {
    border: 1px solid #00f0ff;
    background-color: #0e101e;
}

QPlainTextEdit, QTextEdit {
    background-color: #0a0c16;
    border: 1px solid #1a1e32;
    border-radius: 7px;
    padding: 8px 12px;
    color: #f8fafc;
    font-family: 'JetBrains Mono', 'Cascadia Code', Consolas, monospace;
    font-size: 12px;
    line-height: 1.45;
}
QPlainTextEdit:hover, QTextEdit:hover {
    border-color: #2a3150;
}
QPlainTextEdit:focus, QTextEdit:focus {
    border: 1px solid #00f0ff;
    background-color: #0e101e;
}

/* --- Dropdowns / ComboBoxes --- */
QComboBox {
    background-color: #0a0c16;
    border: 1px solid #1a1e32;
    border-radius: 7px;
    padding: 6px 12px;
    color: #ffffff;
    font-size: 13px;
    min-width: 120px;
}
QComboBox:hover {
    border-color: #a855f7;
}
QComboBox:focus {
    border: 1px solid #00f0ff;
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border-left-width: 0px;
}
QComboBox QAbstractItemView {
    background-color: #080912;
    border: 1px solid #1e2238;
    selection-background-color: #7928ca;
    selection-color: #ffffff;
    color: #f1f5f9;
    padding: 4px;
    outline: none;
}

/* --- Trees & Tables --- */
QTreeWidget {
    background-color: #06070d;
    border: 1px solid #16192a;
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
    background-color: #121424;
    color: #00f0ff;
}
QTreeWidget::item:selected {
    background-color: #7928ca;
    color: #ffffff;
    font-weight: bold;
}

QTableWidget {
    background-color: #04050a;
    border: 1px solid #16192a;
    border-radius: 8px;
    gridline-color: #0f1220;
    color: #e2e8f0;
    selection-background-color: #1f1b3b;
    selection-color: #00f0ff;
}
QTableWidget::item {
    padding: 6px 8px;
    border-bottom: 1px solid #0d0f1b;
}
QTableWidget::item:hover {
    background-color: #0d0f1d;
}
QTableWidget::item:selected {
    background-color: #1a1835;
    color: #00f0ff;
}
QHeaderView::section {
    background-color: #06070e;
    color: #94a3b8;
    padding: 8px;
    border: none;
    border-bottom: 2px solid #16192a;
    font-weight: 700;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

/* --- Tab Navigation --- */
QTabWidget::pane {
    border: 1px solid #16192a;
    background-color: #04050a;
    border-radius: 8px;
    top: -1px;
}
QTabBar::tab {
    background-color: #06070e;
    border: 1px solid #141728;
    border-bottom: none;
    border-top-left-radius: 7px;
    border-top-right-radius: 7px;
    padding: 9px 18px;
    color: #64748b;
    font-size: 12px;
    font-weight: 700;
    margin-right: 4px;
}
QTabBar::tab:hover {
    color: #ffffff;
    background-color: #101322;
}
QTabBar::tab:selected {
    background-color: #04050a;
    border-color: #16192a;
    border-bottom: 2px solid #00f0ff;
    color: #00f0ff;
}

QTabWidget#activity_tab_widget::pane {
    border: 1px solid #16192a;
    background-color: #020306;
    border-radius: 8px;
}
QTabWidget#activity_tab_widget > QWidget {
    background-color: #020306;
}
QTabWidget#activity_tab_widget QTabBar::tab:selected {
    background-color: #020306;
    border-bottom: 2px solid #ff007f;
    color: #ff007f;
}

/* --- SpinBoxes & CheckBoxes --- */
QSpinBox {
    background-color: #0a0c16;
    border: 1px solid #1a1e32;
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
    width: 17px;
    height: 17px;
    border: 1px solid #1e2238;
    border-radius: 4px;
    background-color: #0a0c16;
}
QCheckBox::indicator:unchecked:hover {
    border-color: #00f0ff;
}
QCheckBox::indicator:checked {
    border-color: #00f0ff;
    background-color: #00f0ff;
}

/* --- Sleek Progress Bar --- */
QProgressBar {
    background-color: #0a0c16;
    border: 1px solid #1a1e32;
    border-radius: 6px;
    color: #ffffff;
    font-size: 9pt;
    font-weight: 700;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #7928ca, stop:0.45 #ec4899, stop:1 #00f0ff);
    border-radius: 5px;
}

/* --- Buttons --- */
QPushButton {
    background-color: #0d0f1b;
    border: 1px solid #1e2238;
    border-radius: 7px;
    color: #ffffff;
    padding: 7px 15px;
    font-weight: 600;
    font-size: 12px;
}
QPushButton:hover {
    background-color: #16192d;
    border-color: #00f0ff;
}
QPushButton:pressed {
    background-color: #080912;
}
QPushButton:disabled {
    background-color: #07080f;
    border-color: #141726;
    color: #475569;
}

/* Neon Glow Button Variants */
QPushButton#neon_cyan_btn {
    border: 1px solid #00f0ff;
    color: #00f0ff;
    background-color: rgba(0, 240, 255, 0.07);
    border-radius: 7px;
    font-weight: 700;
}
QPushButton#neon_cyan_btn:hover {
    background-color: #00f0ff;
    color: #000000;
}
QPushButton#neon_cyan_btn:disabled {
    border-color: #16192a;
    color: #475569;
    background-color: transparent;
}

QPushButton#neon_magenta_btn {
    border: 1px solid #ff007f;
    color: #ff007f;
    background-color: rgba(255, 0, 127, 0.07);
    border-radius: 7px;
    font-weight: 700;
}
QPushButton#neon_magenta_btn:hover {
    background-color: #ff007f;
    color: #ffffff;
}

QPushButton#neon_purple_btn {
    border: 1px solid #a855f7;
    color: #c084fc;
    background-color: rgba(168, 85, 247, 0.07);
    border-radius: 7px;
    font-weight: 700;
}
QPushButton#neon_purple_btn:hover {
    background-color: #a855f7;
    color: #ffffff;
}

QPushButton#neon_yellow_btn {
    border: 1px solid #f59e0b;
    color: #fbbf24;
    background-color: rgba(245, 158, 11, 0.07);
    border-radius: 7px;
    font-weight: 700;
}
QPushButton#neon_yellow_btn:hover {
    background-color: #f59e0b;
    color: #000000;
}

/* Large Hero Download Button */
QPushButton#download_btn {
    border: 1px solid #00f0ff;
    color: #ffffff;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #7928ca, stop:0.5 #ec4899, stop:1 #00f0ff);
    font-size: 14px;
    font-weight: 900;
    border-radius: 8px;
    padding: 12px 24px;
    letter-spacing: 1.5px;
}
QPushButton#download_btn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #8b34e2, stop:0.5 #f43f5e, stop:1 #38bdf8);
    color: #000000;
    border-color: #ffffff;
}
QPushButton#download_btn:disabled {
    border-color: #16192a;
    background: #0d0f1b;
    color: #475569;
}

/* Console Logs Area */
QPlainTextEdit#logs_console {
    background-color: #020306;
    border: 1px solid #141728;
    border-radius: 7px;
    color: #38bdf8;
    font-family: 'JetBrains Mono', 'Cascadia Code', Consolas, monospace;
    font-size: 12px;
    line-height: 1.45;
}
"""
