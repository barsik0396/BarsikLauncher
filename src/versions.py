"""
Получение списка версий Minecraft.
Приоритет: сеть -> кэш в конфиге -> захардкоренный список.
"""

import minecraft_launcher_lib
import config as cfg

FALLBACK_VERSIONS = {
    "release":  ["1.12.2", "1.16", "1.16.5", "1.20.1", "1.21.1", "1.21.2", "1.21.4", "1.21.5", "1.21.10", "26.1"],
    "snapshot": [],
    "old_beta": [],
    "old_alpha": [],
}

FABRIC_FALLBACK = ["1.16.5", "1.20.1", "1.21.1", "1.21.2", "1.21.4", "1.21.5"]
FORGE_FALLBACK  = ["1.12.2", "1.16.5", "1.20.1", "1.21.1", "1.21.4"]


def _fetch_from_network() -> tuple[dict, list[str], list[str]]:
    all_versions = minecraft_launcher_lib.utils.get_version_list()

    by_type = {"release": [], "snapshot": [], "old_beta": [], "old_alpha": []}
    for v in all_versions:
        t = v.get("type", "release")
        if t in by_type:
            by_type[t].append(v["id"])

    fabric_versions = [
        v["id"] for v in minecraft_launcher_lib.fabric.get_all_minecraft_versions()
    ]

    forge_versions = minecraft_launcher_lib.forge.list_forge_versions()
    forge_mc = list(dict.fromkeys(v.split("-")[0] for v in forge_versions))

    return by_type, fabric_versions, forge_mc


def load_versions() -> tuple[dict, list[str], list[str]]:
    """
    Возвращает (by_type, fabric_versions, forge_versions).
    by_type = {"release": [...], "snapshot": [...], "old_beta": [...], "old_alpha": [...]}
    """
    try:
        by_type, fabric, forge = _fetch_from_network()
        data = cfg.load()
        data["versions_cache"] = {
            "by_type": by_type,
            "fabric":  fabric,
            "forge":   forge,
        }
        cfg.save(data)
        return by_type, fabric, forge
    except Exception:
        pass

    data = cfg.load()
    cache = data.get("versions_cache")
    if cache:
        return (
            cache.get("by_type", FALLBACK_VERSIONS),
            cache.get("fabric",  FABRIC_FALLBACK),
            cache.get("forge",   FORGE_FALLBACK),
        )

    return FALLBACK_VERSIONS, FABRIC_FALLBACK, FORGE_FALLBACK