import logging
import os
import subprocess

from PySide6.QtCore import QThread, Signal
import minecraft_launcher_lib

logging.basicConfig(
    filename="barsik_debug.log",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s"
)


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

            logging.debug(f"Command: {command}")
            logging.debug(f"PATH: {os.environ.get('PATH')}")

            proc = subprocess.Popen(
                command,
                env=os.environ.copy(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = proc.communicate()
            logging.debug(f"stdout: {stdout.decode(errors='replace')}")
            logging.debug(f"stderr: {stderr.decode(errors='replace')}")

            self.finished.emit()
        except Exception as e:
            logging.exception(f"Error: {e}")
            self.error.emit(str(e))