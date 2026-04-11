import os

from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
BANNER_PNG = os.path.join(ASSETS_DIR, "banner.png")

MAX_WIDTH = 480
MAX_HEIGHT = 270


class SplashScreen(QWidget):
    def __init__(self, on_done, duration_ms: int = 1500):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._label = QLabel()
        self._label.setAlignment(Qt.AlignCenter)

        if os.path.exists(BANNER_PNG):
            pixmap = QPixmap(BANNER_PNG).scaled(
                MAX_WIDTH, MAX_HEIGHT,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self._label.setPixmap(pixmap)
            self.resize(pixmap.width(), pixmap.height())
        else:
            self._label.setText("BarsikLauncher")
            self.resize(400, 200)

        layout.addWidget(self._label)
        self._center()

        QTimer.singleShot(duration_ms, lambda: (self.close(), on_done()))

    def _center(self) -> None:
        screen = self.screen().availableGeometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2,
        )