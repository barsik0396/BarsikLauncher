import sys
import subprocess

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QComboBox, QLineEdit, QPushButton, QStatusBar
)
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QPalette, QColor

import minecraft_launcher_lib


VERSIONS = ["1.21.4", "1.21.10", "26.1"]
MINECRAFT_DIR = minecraft_launcher_lib.utils.get_minecraft_directory()


class LaunchWorker(QThread):
    progress = Signal(int, int, str)
    finished = Signal()
    error = Signal(str)

    def __init__(self, version: str, username: str):
        super().__init__()
        self.version = version
        self.username = username

    def run(self):
        try:
            callback = {
                "setStatus": lambda s: self.progress.emit(0, 0, s),
                "setProgress": lambda v: self.progress.emit(v, 0, ""),
                "setMax": lambda v: self.progress.emit(0, v, ""),
            }
            minecraft_launcher_lib.install.install_minecraft_version(
                self.version, MINECRAFT_DIR, callback=callback
            )
            options = {"username": self.username, "uuid": "", "token": ""}
            command = minecraft_launcher_lib.command.get_minecraft_command(
                self.version, MINECRAFT_DIR, options
            )
            subprocess.Popen(command)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BarsikLauncher")
        self.setFixedSize(340, 160)

        self._launch_worker = None
        self._progress_max = 100

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 8)
        layout.setSpacing(8)

        self.nick_input = QLineEdit()
        self.nick_input.setPlaceholderText("Никнейм")
        self.nick_input.setFixedHeight(32)
        layout.addWidget(self.nick_input)

        self.version_combo = QComboBox()
        self.version_combo.addItems(VERSIONS)
        self.version_combo.setFixedHeight(32)
        layout.addWidget(self.version_combo)

        self.launch_btn = QPushButton("Играть")
        self.launch_btn.setFixedHeight(36)
        self.launch_btn.clicked.connect(self._on_launch)
        layout.addWidget(self.launch_btn)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def _on_launch(self):
        username = self.nick_input.text().strip()
        if not username:
            self.status_bar.showMessage("Введите никнейм")
            return

        version = self.version_combo.currentText()
        self.launch_btn.setEnabled(False)
        self.status_bar.showMessage("Подготовка...")

        self._launch_worker = LaunchWorker(version, username)
        self._launch_worker.progress.connect(self._on_progress)
        self._launch_worker.finished.connect(self._on_finished)
        self._launch_worker.error.connect(self._on_error)
        self._launch_worker.start()

    def _on_progress(self, value: int, maximum: int, status: str):
        if status:
            self.status_bar.showMessage(status)

    def _on_finished(self):
        self.status_bar.showMessage("Игра запущена!")
        self.launch_btn.setEnabled(True)

    def _on_error(self, message: str):
        self.status_bar.showMessage(f"Ошибка: {message[:60]}")
        self.launch_btn.setEnabled(True)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()