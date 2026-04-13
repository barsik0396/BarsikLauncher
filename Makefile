DEB_FOLDER         = 1.0.1-v1.1-n2

.PHONY: deb build
all: help

help:
	@echo "===================================="
	@echo "=== ПОМОЩЬ: BarsikLauncher Make  ==="
	@echo "\033[31mКоманды: "
	@echo "\033[0m - \033[32mhelp\033[0m:       показать эту помощь"
	@echo " - \033[32mbuild\033[0m:      собрать BarsikLauncher из исходников"
	@echo " - \033[32minstall\033[0m:    установить (надо \033[31mзапуск от sudo\033[0m и собранный BarsikLauncher)"
	@echo " - \033[32muninstall\033[0m:  удалить, если установлен из исходников (надо \033[31mзапуск от sudo\033[0m)"
	@echo " - \033[32minfo\033[0m:       информация о BarsikLauncher"
	@echo " - \033[32mclean\033[0m:      удалить build/"
	@echo "===================================="

build:
	@echo "== BarsikLauncher Builder"
	@echo "== Создал: @barsik0396"
	@echo "---> Подготовка к сборке"
	sudo apt install pip
	pip install nuitka PySide6 minecraft_launcher_lib --break-system-packages
	mkdir build
	cp -r src/ build/sources/
	cp -r docs/ build/docs/
	@echo "---> npm install"
	cd build/docs; npm install
	@echo "---> Компиляция документации"
	cd build/docs; npm run build
	@echo "---> Компиляция BarsikLauncher"
	python -m nuitka --onefile --enable-plugin=pyside6 --include-qt-plugins=sensible --follow-imports --include-package-data=minecraft_launcher_lib --include-data-dir=build/sources/assets=assets --output-dir=build/dist build/sources/main.py
	@echo "---> Копирование файлов"
	mkdir build/output
	cp build/dist/main.bin build/output/barsiklauncher
	cp -r build/docs/dist/linux-unpacked/ build/output/docs/
	@echo "---> Компиляция скрипта открытия документации"
	g++ -std=c++17 -o build/barsiklauncher-docs open_docs.cpp
	@echo ""
	@echo "=============================================="
	@echo "\033[32m СБОРКА ЗАВЕРШЕНА\033[0m!"
	@echo "Установить из исходников:\033[32m sudo make install\033[0m"
	@echo " (Для удаления -\033[32m sudo make uninstall\033[0m)"
	@echo "Скомпилированные бинарные файлы и документация -\033[32m build/dist\033[0m"
	@echo "=============================================="

install:
	mkdir /opt/BarsikLauncher-Docs/
	cp -r build/output/docs/ /opt/BarsikLauncher-Docs/
	cp build/output/barsiklauncher /usr/bin/barsiklauncher
	@echo "Установка завершена!"

uninstall:
	rm -rf /opt/BarsikLauncher-Docs/
	rm /usr/bin/barsiklauncher

clean:
	rm -rf build

info:
	@echo "=== BarsikLauncher Builder ==="
	@echo " Версия: 0.1.0"
	@echo " Создал: barsik0396"
	@echo " Лицензия: MIT"
	@echo " Pull Request: #12"