import json
import os

CONFIG_DIR  = os.path.join(os.path.expanduser("~"), ".BarsikLauncher")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

DEFAULTS = {
    "nick":          "",
    "version":       "1.21.4",
    "loader":        None,
    "beta_features": False,
    "versions_cache": None,
}


def load() -> dict:
    if not os.path.exists(CONFIG_FILE):
        return DEFAULTS.copy()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Заполняем отсутствующие ключи дефолтами
        for k, v in DEFAULTS.items():
            data.setdefault(k, v)
        return data
    except Exception:
        return DEFAULTS.copy()


def save(data: dict) -> None:
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)