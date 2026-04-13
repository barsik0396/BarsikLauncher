import os
import subprocess

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QStatusBar, QProgressBar, QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QMovie, QPainter, QPen

from worker import LaunchWorker
from constants import VERSION
import config as cfg
import minecraft_launcher_lib
from versions import load_versions
from version_picker import VersionPickerWindow

ASSETS_DIR  = os.path.join(os.path.dirname(__file__), "assets")
LOADING_GIF = os.path.join(ASSETS_DIR, "loading.gif")

_BY_TYPE, FABRIC_VERSIONS, FORGE_VERSIONS, _SIZES, _LATEST = load_versions()

BASE_HEIGHT = 210
BETA_HEIGHT = 242


class DropButton(QPushButton):
    """QPushButton со стрелкой вниз как у QComboBox."""

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(self.palette().buttonText().color())
        pen.setWidth(2)
        painter.setPen(pen)
        r  = self.rect()
        ax = r.right() - 14
        ay = r.center().y() - 2
        painter.drawLine(ax, ay, ax + 4, ay + 4)
        painter.drawLine(ax + 4, ay + 4, ax + 8, ay)
        painter.end()


class MainWindow(QMainWindow):
    def __init__(self, minecraft_dir: str):
        super().__init__()
        self.minecraft_dir  = minecraft_dir
        self._launch_worker = None
        self._progress_max  = 100
        self._picker_win = None

        self._conf = cfg.load()
        self._selected_version = self._conf.get("version", "1.21.4")
        self._selected_loader  = self._conf.get("loader", None)
        self._beta             = self._conf.get("beta_features", False)

        self._base_h = BETA_HEIGHT if self._beta else BASE_HEIGHT
        self._picker_win = None

        self.setWindowTitle("BarsikLauncher")

        from PySide6.QtWidgets import QApplication
        QApplication.instance().focusChanged.connect(self._on_focus_changed)
        QApplication.instance().installEventFilter(self)
        self.setFixedSize(360, self._base_h)
        self._center()

        central = QWidget()
        self.setCentralWidget(central)
        self._main_layout = QVBoxLayout(central)
        self._main_layout.setContentsMargins(16, 14, 16, 8)
        self._main_layout.setSpacing(8)

        # Top row: nick + version + settings
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        self.nick_input = QLineEdit()
        self.nick_input.setPlaceholderText("Никнейм")
        self.nick_input.setFixedHeight(32)
        self.nick_input.setText(self._conf.get("nick", ""))
        top_row.addWidget(self.nick_input, stretch=3)

        loader_label = f" [{self._selected_loader}]" if self._selected_loader else ""
        self.version_btn = DropButton(f"{self._selected_version}{loader_label}")
        self.version_btn.setFixedHeight(32)
        self.version_btn.setStyleSheet(
            "QPushButton { text-align: left; padding-left: 6px; padding-right: 18px; }"
        )
        self.version_btn.clicked.connect(self._toggle_picker)
        top_row.addWidget(self.version_btn, stretch=2)

        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setFixedSize(32, 32)
        self.settings_btn.clicked.connect(self._open_settings)
        top_row.addWidget(self.settings_btn)

        self._main_layout.addLayout(top_row)

        # Minecraft dir display
        self.path_label = QLabel(self.minecraft_dir)
        self.path_label.setFixedHeight(18)
        self.path_label.setFont(QFont(self.font().family(), 8))
        self.path_label.setStyleSheet("color: gray;")
        self.path_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.path_label.setToolTip(self.minecraft_dir)
        self._main_layout.addWidget(self.path_label)

        # Progress bar + loading gif
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

        self._main_layout.addLayout(progress_row)

        # Beta features
        if self._beta:
            beta_row = QHBoxLayout()
            self.open_dir_btn = QPushButton("📁  Открыть .minecraft")
            self.open_dir_btn.setFixedHeight(30)
            self.open_dir_btn.clicked.connect(self._open_minecraft_dir)
            beta_row.addWidget(self.open_dir_btn)
            self._main_layout.addLayout(beta_row)

        # Launch button
        self.launch_btn = QPushButton("Играть")
        self.launch_btn.setFixedHeight(40)
        self.launch_btn.clicked.connect(self._on_launch)
        self._main_layout.addWidget(self.launch_btn)

        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        self.status_bar.showMessage(f"BarsikLauncher {VERSION}")
        self.setStatusBar(self.status_bar)

    def _toggle_picker(self):
        if self._picker_win and self._picker_win.isVisible():
            self._picker_win.hide()
            return

        installed = minecraft_launcher_lib.utils.get_installed_versions(self.minecraft_dir)
        installed_ids = [v["id"] for v in installed]

        if not self._picker_win:
            self._picker_win = VersionPickerWindow(
                by_type         = _BY_TYPE,
                fabric_versions = FABRIC_VERSIONS,
                forge_versions  = FORGE_VERSIONS,
                latest          = _LATEST,
                installed       = installed_ids,
                current_version = self._selected_version,
                current_loader  = self._selected_loader,
            )
            self._picker_win.version_chosen.connect(self._on_version_chosen)
        else:
            # Обновляем текущую версию чтобы эмодзи обновилось
            self._picker_win.update_current(self._selected_version, self._selected_loader)
            self._picker_win._refresh()

        self._reposition_picker()
        self._picker_win.show()

    def eventFilter(self, obj, event):
        from PySide6.QtCore import QEvent
        if event.type() == QEvent.ApplicationDeactivate:
            if self._picker_win:
                self._picker_win.hide()
        return super().eventFilter(obj, event)

    def _on_focus_changed(self, old, new):
        if not self._picker_win or not self._picker_win.isVisible():
            return
        # Скрываем если фокус ушёл не в пикер и не в лаунчер
        if new is None:
            return
        w = new
        while w is not None:
            if w is self._picker_win or w is self:
                return
            w = w.parent()
        self._picker_win.hide()

    def _reposition_picker(self):
        if self._picker_win:
            btn_pos = self.version_btn.mapToGlobal(self.version_btn.rect().bottomLeft())
            self._picker_win.move(btn_pos)

    def _on_version_chosen(self, vid, loader):
        self._select(vid, loader)

    def _select(self, version: str, loader):
        self._selected_version = version
        self._selected_loader  = loader
        label = f"{version} [{loader}]" if loader else version
        self.version_btn.setText(label)
        self._save_config()

    def closeEvent(self, event):
        if self._picker_win:
            self._picker_win.close()
        self._save_config()
        event.accept()

    def changeEvent(self, event):
        from PySide6.QtCore import QEvent
        if event.type() == QEvent.WindowStateChange:
            if self.isMinimized() and self._picker_win:
                self._picker_win.hide()
        super().changeEvent(event)

    def moveEvent(self, event):
        self._reposition_picker()
        super().moveEvent(event)

    def _center(self) -> None:
        screen = self.screen().availableGeometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2,
        )

    def _open_settings(self):
        from settings import SettingsWindow
        win = SettingsWindow(self)
        win.exec()

    def _open_minecraft_dir(self):
        subprocess.Popen(["xdg-open", self.minecraft_dir])

    def _save_config(self):
        self._conf["nick"]    = self.nick_input.text().strip()
        self._conf["version"] = self._selected_version
        self._conf["loader"]  = self._selected_loader
        cfg.save(self._conf)

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

        self._save_config()

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