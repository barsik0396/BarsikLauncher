import os

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QStatusBar, QProgressBar, QLabel, QMenu
)
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QFont, QMovie, QPainter, QPen, QColor


class DropButton(QPushButton):
    """QPushButton со стрелкой вниз как у QComboBox."""

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        color = self.palette().buttonText().color()
        pen = QPen(color)
        pen.setWidth(2)
        painter.setPen(pen)
        r = self.rect()
        ax = r.right() - 14
        ay = r.center().y() - 2
        painter.drawLine(ax, ay, ax + 4, ay + 4)
        painter.drawLine(ax + 4, ay + 4, ax + 8, ay)
        painter.end()


from worker import LaunchWorker
from constants import VERSION, VERSIONS

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
LOADING_GIF = os.path.join(ASSETS_DIR, "loading.gif")

# Версии MC поддерживаемые модлоадерами
FABRIC_VERSIONS = ["1.16.5", "1.20.1", "1.21.1", "1.21.2", "1.21.4", "1.21.5"]
FORGE_VERSIONS  = ["1.12.2", "1.16.5", "1.20.1", "1.21.1", "1.21.4"]


class MainWindow(QMainWindow):
    def __init__(self, minecraft_dir: str):
        super().__init__()
        self.minecraft_dir = minecraft_dir
        self._launch_worker = None
        self._progress_max = 100

        # Текущий выбор: (version, loader)
        # loader = None | "fabric" | "forge"
        self._selected_version = "1.21.4"
        self._selected_loader = None

        self.setWindowTitle("BarsikLauncher")
        self.setFixedSize(360, 210)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 14, 16, 8)
        layout.setSpacing(8)

        # Nickname + version button side by side
        row = QHBoxLayout()
        row.setSpacing(8)

        self.nick_input = QLineEdit()
        self.nick_input.setPlaceholderText("Никнейм")
        self.nick_input.setFixedHeight(32)
        row.addWidget(self.nick_input, stretch=3)

        self.version_btn = DropButton(self._selected_version)
        self.version_btn.setFixedHeight(32)
        self.version_btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding-left: 6px;
                padding-right: 18px;
            }
        """)
        self.version_btn.clicked.connect(self._open_version_menu)
        row.addWidget(self.version_btn, stretch=2)

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

    def _open_version_menu(self):
        menu = QMenu(self)

        # Обычные версии
        for v in VERSIONS:
            action = menu.addAction(v)
            action.triggered.connect(lambda checked, ver=v: self._select(ver, None))

        menu.addSeparator()

        # Модлоадеры
        modloaders = menu.addMenu("Модлоадеры")

        fabric_menu = modloaders.addMenu("Fabric")
        for v in FABRIC_VERSIONS:
            action = fabric_menu.addAction(v)
            action.triggered.connect(lambda checked, ver=v: self._select(ver, "fabric"))

        forge_menu = modloaders.addMenu("Forge")
        for v in FORGE_VERSIONS:
            action = forge_menu.addAction(v)
            action.triggered.connect(lambda checked, ver=v: self._select(ver, "forge"))

        menu.exec(self.version_btn.mapToGlobal(self.version_btn.rect().bottomLeft()))

    def _select(self, version: str, loader: str | None):
        self._selected_version = version
        self._selected_loader = loader

        if loader:
            self.version_btn.setText(f"{version} [{loader}]")
        else:
            self.version_btn.setText(version)

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

        self.launch_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self._progress_max = 100
        self.status_bar.showMessage("Подготовка...")
        self._set_loading(True)

        self._launch_worker = LaunchWorker(
            self._selected_version,
            username,
            self.minecraft_dir,
            self._selected_loader,
        )
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