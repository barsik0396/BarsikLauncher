import os
import subprocess

from PySide6.QtCore import QThread, Signal
import minecraft_launcher_lib


class LaunchWorker(QThread):
    progress = Signal(int, int, str)
    finished = Signal()
    error = Signal(str)

    def __init__(self, version: str, username: str, minecraft_dir: str, loader: str | None = None):
        super().__init__()
        self.version = version
        self.username = username
        self.minecraft_dir = minecraft_dir
        self.loader = loader

    def _is_installed(self, version_id: str) -> bool:
        installed = minecraft_launcher_lib.utils.get_installed_versions(self.minecraft_dir)
        return any(v["id"] == version_id for v in installed)

    def _callback(self) -> dict:
        return {
            "setStatus":   lambda s: self.progress.emit(0, 0, s),
            "setProgress": lambda v: self.progress.emit(v, 0, ""),
            "setMax":      lambda v: self.progress.emit(0, v, ""),
        }

    def _install_fabric(self) -> str:
        self.progress.emit(0, 0, "Получение версии Fabric...")
        loader_version = minecraft_launcher_lib.fabric.get_latest_loader_version()
        version_id = f"fabric-loader-{loader_version}-{self.version}"

        if not self._is_installed(version_id):
            self.progress.emit(0, 0, "Установка Fabric...")
            minecraft_launcher_lib.fabric.install_fabric(
                self.version, self.minecraft_dir,
                loader_version=loader_version,
                callback=self._callback(),
            )

        return version_id

    def _install_forge(self) -> str:
        self.progress.emit(0, 0, "Получение версии Forge...")
        forge_version = minecraft_launcher_lib.forge.find_forge_version(self.version)
        if not forge_version:
            raise RuntimeError(f"Forge не найден для {self.version}")

        version_id = f"{self.version}-forge-{forge_version.split('-', 1)[-1]}"

        if not self._is_installed(version_id):
            self.progress.emit(0, 0, "Установка Forge...")
            minecraft_launcher_lib.forge.install_forge_version(
                forge_version, self.minecraft_dir,
                callback=self._callback(),
            )

        return version_id

    def run(self):
        try:
            # Установка базовой версии MC если нужно
            if not self._is_installed(self.version):
                minecraft_launcher_lib.install.install_minecraft_version(
                    self.version, self.minecraft_dir, callback=self._callback()
                )

            # Установка модлоадера и получение финального version_id
            if self.loader == "fabric":
                launch_version = self._install_fabric()
            elif self.loader == "forge":
                launch_version = self._install_forge()
            else:
                launch_version = self.version

            options = {"username": self.username, "uuid": "", "token": ""}
            command = minecraft_launcher_lib.command.get_minecraft_command(
                launch_version, self.minecraft_dir, options
            )

            subprocess.Popen(command, env=os.environ.copy())
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))