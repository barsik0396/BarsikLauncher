DEB_FOLDER         = 1.0.1-v1.1-n2
BUILDER            = python3 -m nuitka
BUILDER_FLAGS_1    = --onefile --enable-plugin=pyside6 --include-qt-plugins=sensible --follow-imports --output-dir=build/dist
BUILDER_MAIN       = build/sources/main.py
BUILDER_FLAGS_2    = --include-package-data=minecraft_launcher_lib 
MAKE_DIST          = ${BUILDER} ${BUILDER_FLAGS_1} ${BUILDER_MAIN} ${BUILDER_FLAGS_2}

.PHONY: deb
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
	@echo "===================================="
	@mkdir ~/.barsiklauncher-mktmp
	@echo "]]]]]]]]]]]]" > ~/.barsiklauncher-mktmp/ed894u3
	@rm -rf ~/.barsiklauncher-mktmp

build:
	@echo "== BarsikLauncher Builder"
	@echo "== Создал: @barsik0396"
	@echo "== PR сборщика: #10"
	@echo ""
	@echo "--> (30) Подготовка к сборке"
	@echo "1: BLMake-WARN (31): "
	@echo "2: BLMake-WARN (32): Сейчас происходит установка зависимостей для"
	@echo "3: BLMake-WARN (33): Сборки, потребуется пароль."
	@echo "4: BLMake-WARN (34): "
	sudo apt install pip
	mkdir build
	pip install nuitka --break-system-packages 
	pip install PySide6 minecraft_launcher_lib
	cp -r src/ build/sources/
	@echo "--> (40) Сборка"
	${MAKE_DIST}
	@echo "--> (42) Подготовка к сборке документации"