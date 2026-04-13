import os
import sys
import subprocess

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QCheckBox, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt

import config as cfg


class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.setFixedSize(300, 120)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self._data = cfg.load()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 12)
        layout.setSpacing(12)

        # Переключатель режима новых фич
        row = QHBoxLayout()
        label = QLabel("Режим новых фич")
        self._checkbox = QCheckBox()
        self._checkbox.setChecked(self._data.get("beta_features", False))
        row.addWidget(label)
        row.addStretch()
        row.addWidget(self._checkbox)
        layout.addLayout(row)

        layout.addStretch()

        # Кнопки
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        save_btn = QPushButton("Сохранить")
        save_btn.setFixedHeight(30)
        save_btn.clicked.connect(self._on_save)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _on_save(self):
        new_beta = self._checkbox.isChecked()
        old_beta = self._data.get("beta_features", False)

        self._data["beta_features"] = new_beta
        cfg.save(self._data)

        if new_beta != old_beta:
            msg = QMessageBox(self)
            msg.setWindowTitle("Перезапуск")
            msg.setText("Для применения изменений нужно перезапустить лаунчер.")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msg.setDefaultButton(QMessageBox.Ok)
            if msg.exec() == QMessageBox.Ok:
                self._restart()
        else:
            self.accept()

    def _restart(self):
        args = [sys.executable] + sys.argv + ["--skip-splash"]
        subprocess.Popen(args)
        sys.exit(0)