"""
Получение списка версий Minecraft.
Приоритет: сеть -> кэш в конфиге -> захардкоренный список.
"""

import minecraft_launcher_lib
import config as cfg

FALLBACK_VERSIONS = {
    "release":   ["1.12.2", "1.16", "1.16.5", "1.20.1", "1.21.1", "1.21.2", "1.21.4", "1.21.5", "1.21.10", "26.1"],
    "snapshot":  [],
    "old_beta":  [],
    "old_alpha": [],
}

FABRIC_FALLBACK = ["1.16.5", "1.20.1", "1.21.1", "1.21.2", "1.21.4", "1.21.5"]
FORGE_FALLBACK  = ["1.12.2", "1.16.5", "1.20.1", "1.21.1", "1.21.4"]


def _fetch_from_network() -> tuple[dict, list[str], list[str], dict, dict]:
    all_versions = minecraft_launcher_lib.utils.get_version_list()

    by_type  = {"release": [], "snapshot": [], "old_beta": [], "old_alpha": []}
    sizes    = {}   # version_id -> bytes (размер клиента)
    latest   = {}   # "release" -> id, "snapshot" -> id

    # latest из манифеста
    try:
        import requests
        manifest = requests.get(
            "https://launchermeta.mojang.com/mc/game/version_manifest_v2.json",
            timeout=5
        ).json()
        latest = manifest.get("latest", {})
    except Exception:
        pass

    for v in all_versions:
        t = v.get("type", "release")
        if t in by_type:
            by_type[t].append(v["id"])

        # Размер клиента — берём из поля downloads если доступно
        dl = v.get("downloads", {})
        client = dl.get("client", {})
        if client.get("size"):
            sizes[v["id"]] = client["size"]

    fabric_versions = [
        v["version"] for v in minecraft_launcher_lib.fabric.get_all_minecraft_versions()
    ]

    forge_versions = minecraft_launcher_lib.forge.list_forge_versions()
    forge_mc = list(dict.fromkeys(v.split("-")[0] for v in forge_versions))

    return by_type, fabric_versions, forge_mc, sizes, latest


def load_versions() -> tuple[dict, list[str], list[str], dict, dict]:
    """
    Возвращает (by_type, fabric_versions, forge_versions, sizes, latest).
    by_type = {"release": [...], "snapshot": [...], "old_beta": [...], "old_alpha": [...]}
    sizes   = {version_id: bytes}
    latest  = {"release": "...", "snapshot": "..."}
    """
    try:
        by_type, fabric, forge, sizes, latest = _fetch_from_network()
        data = cfg.load()
        data["versions_cache"] = {
            "by_type": by_type,
            "fabric":  fabric,
            "forge":   forge,
            "sizes":   sizes,
            "latest":  latest,
        }
        cfg.save(data)
        return by_type, fabric, forge, sizes, latest
    except Exception:
        pass

    data  = cfg.load()
    cache = data.get("versions_cache")
    if cache:
        return (
            cache.get("by_type", FALLBACK_VERSIONS),
            cache.get("fabric",  FABRIC_FALLBACK),
            cache.get("forge",   FORGE_FALLBACK),
            cache.get("sizes",   {}),
            cache.get("latest",  {}),
        )

    return FALLBACK_VERSIONS, FABRIC_FALLBACK, FORGE_FALLBACK, {}, {}