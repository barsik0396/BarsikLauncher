# 🐱 BarsikLauncher

<div align="center">

**Простой. Быстрый. Бесплатный.**
Minecraft-лаунчер для Linux, который не мешает играть.

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

</div>

---

## 🎮 Почему BarsikLauncher?

Большинство Minecraft-лаунчеров перегружены: аккаунты, моды, профили, облака, подписки...
BarsikLauncher делает ровно одно — **запускает Minecraft**. Без лишнего.

| | 🐱 BarsikLauncher | TLauncher | KLauncher | MultiMC |
|---|---|---|---|---|
| 💸 Цена | Бесплатно | Бесплатно | Бесплатно | Бесплатно |
| 🐧 Платформа | Linux | Windows, macOS, Linux | Windows, Linux | Windows, macOS, Linux |
| ⚡ Интерфейс | Минималистичный | Перегруженный | Чуть перегруженный | Средний |
| 📢 Реклама | Нет | Много | Серверы и автодобавление | Нет |
| 🔓 Тип | Open-source | Закрытый | Закрытый | Open-source |
| 🌍 Популярность | Низкая | Очень высокая | Нормальная | Высокая |
| 🎨 Кастомизация | Минимальная | Нет | Минимальная | Высокая |

---

## 📸 Скриншоты

![Главная страница](https://barsiklauncher.pages.dev/assets/main_page.png)

---

## 🚀 Установка

### Binary (рекомендуется)

```bash
# Скачать бинарку
wget https://github.com/barsik0396/BarsikLauncher/releases/download/1.0.0-stable%2Bblapi-v1.0/BarsikLauncher

# Дать права на выполнение
chmod +x BarsikLauncher

# Запустить
./BarsikLauncher
```

### From source

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

---

## 🛠 Requirements

- Python 3.x
- Зависимости из `requirements.txt` (`pip install -r requirements.txt --break-system-packages`)

---

## ❓ FAQ

**Лаунчер бесплатный?**
Да, полностью. Без скрытых платежей и подписок.

**Поддерживается ли Windows / macOS?**
Нет. BarsikLauncher разработан исключительно для Linux.

**Нужен аккаунт для игры?**
Нет. BarsikLauncher работает в офлайн-режиме — авторизация не требуется.

**Что такое blapi?**
BarsikLauncher API — внутренняя библиотека, на которой работает лаунчер.

---

## 🤝 Участие в разработке

Хочешь помочь проекту? Читай [CONTRIBUTING.md](CONTRIBUTING.md) — там всё, что нужно знать.

## 🔒 Безопасность

Нашёл уязвимость? Не создавай публичный Issue — читай [SECURITY.md](SECURITY.md).

## 📋 Changelog

История всех изменений — в [CHANGELOG.md](CHANGELOG.md).

---

<div align="center">

Сделано с ❤️ и 🐱

</div>