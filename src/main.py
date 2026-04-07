"""
BarsikLauncher 1.0.1-nightly-1+blapi-v1.1
"""

import sys
import subprocess

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QLineEdit, QPushButton, QStatusBar, QProgressBar, QLabel
)
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QFont

import minecraft_launcher_lib


VERSION = "1.0.1-nightly-1+blapi-v1.1"

VERSIONS = [
    "1.12.2",
    "1.16",
    "1.16.5",
    "1.20.1",
    "1.21.1",
    "1.21.2",
    "1.21.4",
    "1.21.5",
    "1.21.10",
    "26.1",
]

# ANSI colors
C_RESET  = "\033[0m"
C_BOLD   = "\033[1m"
C_CYAN   = "\033[96m"
C_GREEN  = "\033[92m"
C_YELLOW = "\033[93m"
C_GRAY   = "\033[90m"


def print_help() -> None:
    versions_str = ", ".join(VERSIONS)
    print(f"""
{C_CYAN}{C_BOLD}BarsikLauncher{C_RESET} {C_GRAY}{VERSION}{C_RESET}
{C_GRAY}Простой Minecraft-лаунчер для Linux{C_RESET}

{C_BOLD}Использование:{C_RESET}
  {C_GREEN}python main.py{C_RESET} {C_YELLOW}[опции]{C_RESET}

{C_BOLD}Опции:{C_RESET}
  {C_YELLOW}-p{C_RESET}, {C_YELLOW}--path{C_RESET} {C_CYAN}<путь>{C_RESET}   Путь к папке Minecraft
                       {C_GRAY}(по умолчанию: ~/.minecraft){C_RESET}
  {C_YELLOW}-h{C_RESET}, {C_YELLOW}--help{C_RESET}          Показать это сообщение

{C_BOLD}Доступные версии:{C_RESET}
  {C_GRAY}{versions_str}{C_RESET}
""")


def parse_args() -> tuple[str | None]:
    args = sys.argv[1:]
    minecraft_path = None

    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("-h", "--help"):
            print_help()
            sys.exit(0)
        elif arg in ("-p", "--path"):
            i += 1
            if i >= len(args):
                print(f"{C_YELLOW}Ошибка:{C_RESET} флаг -p требует аргумент <путь>")
                sys.exit(1)
            minecraft_path = args[i]
        else:
            print(f"{C_YELLOW}Неизвестный аргумент:{C_RESET} {arg}")
            print(f"Используй {C_GREEN}-h{C_RESET} для справки.")
            sys.exit(1)
        i += 1

    return minecraft_path


class LaunchWorker(QThread):
    progress = Signal(int, int, str)
    finished = Signal()
    error = Signal(str)

    def __init__(self, version: str, username: str, minecraft_dir: str):
        super().__init__()
        self.version = version
        self.username = username
        self.minecraft_dir = minecraft_dir

    def run(self):
        try:
            callback = {
                "setStatus":   lambda s: self.progress.emit(0, 0, s),
                "setProgress": lambda v: self.progress.emit(v, 0, ""),
                "setMax":      lambda v: self.progress.emit(0, v, ""),
            }
            minecraft_launcher_lib.install.install_minecraft_version(
                self.version, self.minecraft_dir, callback=callback
            )
            options = {"username": self.username, "uuid": "", "token": ""}
            command = minecraft_launcher_lib.command.get_minecraft_command(
                self.version, self.minecraft_dir, options
            )
            subprocess.Popen(command)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self, minecraft_dir: str):
        super().__init__()
        self.minecraft_dir = minecraft_dir
        self._launch_worker = None
        self._progress_max = 100

        self.setWindowTitle("BarsikLauncher")
        self.setFixedSize(360, 210)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 14, 16, 8)
        layout.setSpacing(8)

        # Nickname + version side by side
        row = QHBoxLayout()
        row.setSpacing(8)

        self.nick_input = QLineEdit()
        self.nick_input.setPlaceholderText("Никнейм")
        self.nick_input.setFixedHeight(32)
        row.addWidget(self.nick_input, stretch=3)

        self.version_combo = QComboBox()
        self.version_combo.addItems(VERSIONS)
        self.version_combo.setCurrentText("1.21.4")
        self.version_combo.setFixedHeight(32)
        row.addWidget(self.version_combo, stretch=2)

        layout.addLayout(row)

        # Minecraft dir display
        self.path_label = QLabel(self.minecraft_dir)
        self.path_label.setFixedHeight(18)
        self.path_label.setFont(QFont(self.font().family(), 8))
        self.path_label.setStyleSheet("color: gray;")
        self.path_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.path_label.setToolTip(self.minecraft_dir)
        layout.addWidget(self.path_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(100)
        layout.addWidget(self.progress_bar)

        # Launch button
        self.launch_btn = QPushButton("Играть")
        self.launch_btn.setFixedHeight(40)
        self.launch_btn.clicked.connect(self._on_launch)
        layout.addWidget(self.launch_btn)

        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        self.status_bar.showMessage(f"BarsikLauncher {VERSION}")
        self.setStatusBar(self.status_bar)

    def _on_launch(self):
        username = self.nick_input.text().strip()
        if not username:
            self.status_bar.showMessage("Введите никнейм")
            return

        version = self.version_combo.currentText()
        self.launch_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self._progress_max = 100
        self.status_bar.showMessage("Подготовка...")

        self._launch_worker = LaunchWorker(version, username, self.minecraft_dir)
        self._launch_worker.progress.connect(self._on_progress)
        self._launch_worker.finished.connect(self._on_finished)
        self._launch_worker.error.connect(self._on_error)
        self._launch_worker.start()

    def _on_progress(self, value: int, maximum: int, status: str):
        if maximum > 0:
            self._progress_max = maximum
            self.progress_bar.setMaximum(maximum)
        if value > 0:
            self.progress_bar.setValue(value)
        if status:
            self.status_bar.showMessage(status)

    def _on_finished(self):
        self.progress_bar.setValue(self._progress_max)
        self.status_bar.showMessage("Игра запущена!")
        self.launch_btn.setEnabled(True)

    def _on_error(self, message: str):
        self.status_bar.showMessage(f"Ошибка: {message[:70]}")
        self.launch_btn.setEnabled(True)


def main():
    minecraft_path = parse_args()
    minecraft_dir = minecraft_path or minecraft_launcher_lib.utils.get_minecraft_directory()

    app = QApplication(sys.argv)
    window = MainWindow(minecraft_dir)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()