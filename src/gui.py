import os

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QLineEdit, QPushButton, QStatusBar, QProgressBar, QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QMovie

from worker import LaunchWorker
from constants import VERSION, VERSIONS

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
LOADING_GIF = os.path.join(ASSETS_DIR, "loading.gif")


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

        # Progress bar + loading gif side by side
        progress_row = QHBoxLayout()
        progress_row.setSpacing(6)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(100)
        progress_row.addWidget(self.progress_bar)

        self.loading_label = QLabel()
        self.loading_label.setFixedSize(18, 18)
        self.loading_label.setVisible(False)
        progress_row.addWidget(self.loading_label)

        self._movie = None
        if os.path.exists(LOADING_GIF):
            self._movie = QMovie(LOADING_GIF)
            self._movie.setScaledSize(self.loading_label.size())
            self._movie.setSpeed(200)
            self.loading_label.setMovie(self._movie)

        layout.addLayout(progress_row)

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

    def _set_loading(self, active: bool) -> None:
        self.loading_label.setVisible(active)
        if self._movie:
            if active:
                self._movie.start()
            else:
                self._movie.stop()

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
        self._set_loading(True)

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
        self._set_loading(False)
        self.progress_bar.setValue(self._progress_max)
        self.status_bar.showMessage("Игра запущена!")
        self.launch_btn.setEnabled(True)

    def _on_error(self, message: str):
        self._set_loading(False)
        self.status_bar.showMessage(f"Ошибка: {message[:70]}")
        self.launch_btn.setEnabled(True)