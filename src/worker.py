import os
import subprocess

from PySide6.QtCore import QThread, Signal
import minecraft_launcher_lib


class LaunchWorker(QThread):
    progress = Signal(int, int, str)
    finished = Signal()
    error = Signal(str)

    def __init__(self, version: str, username: str, minecraft_dir: str):
        super().__init__()
        self.version = version
        self.username = username
        self.minecraft_dir = minecraft_dir

    def _is_installed(self) -> bool:
        installed = minecraft_launcher_lib.utils.get_installed_versions(self.minecraft_dir)
        return any(v["id"] == self.version for v in installed)

    def run(self):
        try:
            if not self._is_installed():
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

            subprocess.Popen(command, env=os.environ.copy())
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))