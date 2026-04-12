"""
Получение списка версий Minecraft.
Приоритет: сеть -> кэш в конфиге -> захардкоренный список.
"""

import minecraft_launcher_lib
import config as cfg

# Захардкоренный fallback
FALLBACK_VERSIONS = [
    "1.12.2",
    "1.16",
    "1.16.5",
    "1.20.1",
    "1.21.1",
    "1.21.2",
    "1.21.4",
    "1.21.5",
    "1.21.10",
    "26.1",
]

FABRIC_FALLBACK = ["1.16.5", "1.20.1", "1.21.1", "1.21.2", "1.21.4", "1.21.5"]
FORGE_FALLBACK  = ["1.12.2", "1.16.5", "1.20.1", "1.21.1", "1.21.4"]


def _fetch_from_network() -> tuple[list[str], list[str], list[str]]:
    """Получает все версии MC, Fabric-совместимые и Forge-совместимые из сети."""
    all_versions = minecraft_launcher_lib.utils.get_version_list()

    mc_versions = [v["id"] for v in all_versions]

    fabric_versions = [
        v["id"]
        for v in minecraft_launcher_lib.fabric.get_all_minecraft_versions()
        if v.get("stable", False) or True
    ]

    forge_versions = minecraft_launcher_lib.forge.list_forge_versions()
    forge_mc = list(dict.fromkeys(v.split("-")[0] for v in forge_versions))

    return mc_versions, fabric_versions, forge_mc


def load_versions() -> tuple[list[str], list[str], list[str]]:
    """
    Возвращает (mc_versions, fabric_versions, forge_versions).
    Обновляет кэш в конфиге при успешном получении из сети.
    """
    try:
        mc, fabric, forge = _fetch_from_network()
        data = cfg.load()
        data["versions_cache"] = {
            "mc":     mc,
            "fabric": fabric,
            "forge":  forge,
        }
        cfg.save(data)
        return mc, fabric, forge
    except Exception:
        pass

    # Пробуем кэш из конфига
    data = cfg.load()
    cache = data.get("versions_cache")
    if cache:
        return (
            cache.get("mc",     FALLBACK_VERSIONS),
            cache.get("fabric", FABRIC_FALLBACK),
            cache.get("forge",  FORGE_FALLBACK),
        )

    # Полный fallback
    return FALLBACK_VERSIONS, FABRIC_FALLBACK, FORGE_FALLBACK