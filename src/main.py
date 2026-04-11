"""
BarsikLauncher 1.0.1-nightly-2+blapi-v1.1
"""

import sys

from PySide6.QtWidgets import QApplication
import minecraft_launcher_lib

from constants import VERSION, VERSIONS, C_RESET, C_BOLD, C_CYAN, C_GREEN, C_YELLOW, C_GRAY
from gui import MainWindow
from splash import SplashScreen


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
  {C_YELLOW}-s{C_RESET}, {C_YELLOW}--skip-splash{C_RESET}   Пропустить баннер при запуске
  {C_YELLOW}-h{C_RESET}, {C_YELLOW}--help{C_RESET}          Показать это сообщение

{C_BOLD}Доступные версии:{C_RESET}
  {C_GRAY}{versions_str}{C_RESET}
""")


def parse_args() -> tuple[str | None, bool]:
    args = sys.argv[1:]
    minecraft_path = None
    skip_splash = False

    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("-s", "--skip-splash"):
            skip_splash = True
        elif arg in ("-h", "--help"):
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

    return minecraft_path, skip_splash


def main():
    minecraft_path, skip_splash = parse_args()
    minecraft_dir = minecraft_path or minecraft_launcher_lib.utils.get_minecraft_directory()

    app = QApplication(sys.argv)

    window = MainWindow(minecraft_dir)
    if skip_splash:
        window.show()
    else:
        splash = SplashScreen(on_done=window.show, duration_ms=1500)
        splash.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()