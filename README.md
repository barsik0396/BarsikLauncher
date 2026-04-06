# 🐱 BarsikLauncher

> Лаунчер для Minecraft на Python

[![Version](https://img.shields.io/badge/version-1.0.0--stable-brightgreen)](https://github.com/barsik0396/BarsikLauncher/releases)
[![API Version](https://img.shields.io/badge/blapi-v1.0-blue)](https://github.com/barsik0396/BarsikLauncher)
[![Status](https://img.shields.io/badge/status-active-success)](https://github.com/barsik0396/BarsikLauncher)
[![Platform](https://img.shields.io/badge/platform-Linux-orange?logo=linux)](https://github.com/barsik0396/BarsikLauncher)
[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Releases](https://img.shields.io/github/v/release/barsik0396/BarsikLauncher)](https://github.com/barsik0396/BarsikLauncher/releases)
[![Issues](https://img.shields.io/github/issues/barsik0396/BarsikLauncher)](https://github.com/barsik0396/BarsikLauncher/issues)
[![Pull Requests](https://img.shields.io/github/issues-pr/barsik0396/BarsikLauncher)](https://github.com/barsik0396/BarsikLauncher/pulls)
[![Stars](https://img.shields.io/github/stars/barsik0396/BarsikLauncher)](https://github.com/barsik0396/BarsikLauncher/stargazers)
[![Forks](https://img.shields.io/github/forks/barsik0396/BarsikLauncher)](https://github.com/barsik0396/BarsikLauncher/network/members)

## 📖 О проекте

BarsikLauncher — простой и бесплатный Minecraft-лаунчер для Linux. Никаких лишних функций: только выбор версии, ввод ника и запуск игры. Написан на Python с использованием PySide6 для интерфейса и minecraft_launcher_lib для запуска Minecraft.

## 🚀 Установка

### Бинарка (рекомендуется)

```bash
# Скачать бинарку
wget https://github.com/barsik0396/BarsikLauncher/releases/download/1.0.0-stable%2Bblapi-v1.0/BarsikLauncher

# Дать права на выполнение
chmod +x BarsikLauncher

# Запустить
./BarsikLauncher
```

### Из исходников

```bash
# Клонировать репозиторий
git clone https://github.com/barsik0396/BarsikLauncher.git
cd BarsikLauncher

# Установить зависимости
pip install -r requirements.txt --break-system-packages
pip install pyinstaller --break-system-packages

# Собрать бинарку
pyinstaller --onefile --name BarsikLauncher main.py

# Запустить
cd dist
chmod +x BarsikLauncher
./BarsikLauncher
```

## 🛠 Требования

- Python 3.x
- Зависимости из `requirements.txt` (`pip install -r requirements.txt --break-system-packages`)

## 🤝 Участие в разработке

Хочешь помочь? Читай [CONTRIBUTING.md](CONTRIBUTING.md).

## 🔒 Безопасность

Нашёл уязвимость? Читай [SECURITY.md](SECURITY.md).

## 📋 Changelog

История изменений — в [CHANGELOG.md](CHANGELOG.md).