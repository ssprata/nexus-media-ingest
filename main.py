import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt, pyqtSignal

from ui.main_window import MainWindow, ToolDownloadWorker, CyberMessageBox
from ui.styles import CYBERPUNK_STYLE
from dependency_manager import DependencyManager

class FirstTimeSetupWindow(QWidget):
    finished = pyqtSignal()

    def __init__(self, dep_manager):
        super().__init__()
        self.dep_manager = dep_manager
        self.setWindowTitle("Nexus — Initializing Engines...")
        self.setFixedSize(500, 250)
        
        # Frameless glowing window
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet(CYBERPUNK_STYLE)
        
        # Enable border glow style via custom property or border
        self.setObjectName("card_frame")
        
        self.setup_ui()
        
        self.to_download = []
        if not self.dep_manager.is_installed("aria2c"):
            self.to_download.append("aria2c")
        if not self.dep_manager.is_installed("yt-dlp"):
            self.to_download.append("yt-dlp")
        if not self.dep_manager.is_installed("ffmpeg"):
            self.to_download.append("ffmpeg")
            
        self.current_download_idx = 0
        self.active_worker = None

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 45, 40, 45)
        layout.setSpacing(20)

        # Glowing Neon title
        self.title_lbl = QLabel("INITIALIZING NEXUS INGEST")
        self.title_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #ff007f; letter-spacing: 2px;")
        self.title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_lbl)

        self.status_lbl = QLabel("Checking workspace dependencies...")
        self.status_lbl.setStyleSheet("color: #00f0ff; font-size: 13px;")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_lbl)

        # Neon styled progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(18)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

    def start_downloads(self):
        if not self.to_download:
            self.finished.emit()
            return
        
        self.download_next()

    def download_next(self):
        if self.current_download_idx >= len(self.to_download):
            self.finished.emit()
            return

        tool = self.to_download[self.current_download_idx]
        self.status_lbl.setText(f"Downloading required engine: '{tool}'...")
        self.progress_bar.setValue(0)

        self.active_worker = ToolDownloadWorker(self.dep_manager, tool)
        self.active_worker.progress_updated.connect(self.on_progress)
        self.active_worker.completed.connect(self.on_completed)
        self.active_worker.start()

    def on_progress(self, tool, percentage):
        self.progress_bar.setValue(int(percentage))

    def on_completed(self, tool, success, error_msg):
        self.active_worker.quit()
        self.active_worker.wait()
        
        if success:
            self.current_download_idx += 1
            self.download_next()
        else:
            CyberMessageBox.show_info(
                self, "Initialization Error", 
                f"Failed to download required dependency '{tool}':\n{error_msg}\n\nPlease check your connection and try again.",
                border_color="#ff007f"
            )
            sys.exit(1)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("nexus-media-ingest")
    app.setApplicationDisplayName("Nexus")
    app.setStyleSheet(CYBERPUNK_STYLE)

    dep_manager = DependencyManager()

    # If core dependencies are missing, show the setup screen
    if not dep_manager.check_core_dependencies():
        setup_win = FirstTimeSetupWindow(dep_manager)
        
        main_win = None
        
        def on_setup_finished():
            nonlocal main_win
            setup_win.close()
            main_win = MainWindow()
            main_win.show()
            
        setup_win.finished.connect(on_setup_finished)
        setup_win.show()
        setup_win.start_downloads()
    else:
        # Launch directly
        main_win = MainWindow()
        main_win.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
