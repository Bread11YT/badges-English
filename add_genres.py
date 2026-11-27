"""Добавляет категорию «Жанры» (25 бейджей) в badges.json и пересобирает всё.

Положите этот файл рядом с build.py и badges.json, затем:
    python add_genres.py

Иконки встроены прямо в бейджи (поле "svg"), поэтому папку icons/ трогать не нужно.
Скрипт можно запускать повторно: категория просто обновится.
"""
import json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CFG = ROOT / "badges.json"

# Все иконки нарисованы в сетке 24x24 одним цветом.
def gear():
    teeth = "".join(
        f'<path d="M10.5 1h3v4h-3z" transform="rotate({a} 12 12)"/>' for a in range(0, 360, 45))
    body = '<path d="M12 5a7 7 0 1 0 0 14 7 7 0 0 0 0-14zm0 4a3 3 0 1 1 0 6 3 3 0 0 1 0-6z" fill-rule="evenodd"/>'
    return teeth + body

ICONS = {
 "tower-defense": '<path d="M5 3h3v2h2V3h4v2h2V3h3v7h-2v11h-5v-5h-2v5H7V10H5z"/>',
 "rpg": '<path d="M12 2l2 3v9h-4V5zM7 14h10v2H7zM11 16h2v4h-2zM10.5 20h3v2h-3z"/>',
 "roguelike": '<path fill-rule="evenodd" d="M5 3h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2zM8 6.5a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3zm8 0a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3zM12 10.5a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3zM8 14.5a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3zm8 0a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3z"/>',
 "platformer": '<path d="M3 21v-5h5v-5h5V6h8v15z"/>',
 "shooter": '<path d="M12 4a8 8 0 1 0 0 16 8 8 0 0 0 0-16zm0 2a6 6 0 1 1 0 12 6 6 0 0 1 0-12z" fill-rule="evenodd"/><path d="M11 1h2v3h-2zM11 20h2v3h-2zM1 11h3v2H1zM20 11h3v2h-3zM12 10.5a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3z"/>',
 "strategy": '<path d="M12 4a3 3 0 1 0 0 6 3 3 0 0 0 0-6zM9 11h6l-1 4 2 2v2H8v-2l2-2zM6 20h12v2H6z"/>',
 "survival": '<path d="M12 2c1 4 6 6 6 12a6 6 0 0 1-12 0c0-3 1.5-4.5 3-6 0 2 1 3 2 3 0-3-1-5 1-9z"/>',
 "sandbox": '<path d="M12 2 3 7v10l9 5 9-5V7l-9-5zm0 2.3L18.7 8 12 11.7 5.3 8 12 4.3zM5 9.6l6 3.3v6.5l-6-3.3V9.6zm8 9.8v-6.5l6-3.3v6.5l-6 3.3z"/>',
 "puzzle": '<path d="M20.5 11H19V7c0-1.1-.9-2-2-2h-4V3.5a2.5 2.5 0 0 0-5 0V5H4c-1.1 0-2 .9-2 2v3.8h1.5c1.5 0 2.7 1.2 2.7 2.7s-1.2 2.7-2.7 2.7H2V20c0 1.1.9 2 2 2h3.8v-1.5c0-1.5 1.2-2.7 2.7-2.7s2.7 1.2 2.7 2.7V22H17c1.1 0 2-.9 2-2v-4h1.5a2.5 2.5 0 0 0 0-5z"/>',
 "horror": '<path fill-rule="evenodd" d="M12 2a8 8 0 0 0-8 8c0 2.5 1.2 4.4 3 5.7V19a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1v-3.3c1.8-1.3 3-3.2 3-5.7a8 8 0 0 0-8-8zM8.5 9a2 2 0 1 0 0 4 2 2 0 0 0 0-4zm7 0a2 2 0 1 0 0 4 2 2 0 0 0 0-4zM12 14l-1 2h2z"/>',
 "racing": '<path d="M5 2h2v20H5zM7 3h13l-3 4.5 3 4.5H7z"/>',
 "simulation": gear(),
 "idle-clicker": '<path d="M5 3l14 8-6 2 4 7-3 1.5-4-7-5 4z"/>',
 "card-game": '<path fill-rule="evenodd" d="M7 3h10a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2zM12 7l4 5-4 5-4-5z"/>',
 "fighting": '<path d="M13 2 4 14h6l-1 8 9-12h-6z"/>',
 "adventure": '<path d="M3 20 9 9l4 6 3-4 5 9z"/>',
 "open-world": '<path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm0 2a8 8 0 1 1 0 16 8 8 0 0 1 0-16z" fill-rule="evenodd"/><path d="M16 8l-2.5 5.5L8 16l2.5-5.5z"/>',
 "mmo": '<path d="M9 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm8 0a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5zM9 13c-3 0-6 1.5-6 4v2h12v-2c0-2.5-3-4-6-4zm8 0c-.5 0-1 0-1.5.1 1.2.9 2 2.2 2 3.9v2h4.5v-2c0-2-2.5-4-5-4z"/>',
 "battle-royale": '<path d="M3 8l4 4 5-7 5 7 4-4-2 11H5z"/>',
 "moba": '<path d="M12 2 4 5v6c0 5 3.4 9.7 8 11 4.6-1.3 8-6 8-11V5z"/>',
 "stealth": '<path fill-rule="evenodd" d="M12 5C7 5 2.7 8.1 1 12c1.7 3.9 6 7 11 7s9.3-3.1 11-7c-1.7-3.9-6-7-11-7zm0 11a4 4 0 1 1 0-8 4 4 0 0 1 0 8zM12 10a2 2 0 1 0 0 4 2 2 0 0 0 0-4z"/>',
 "rhythm": '<path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/>',
 "visual-novel": '<path d="M3 4h8c.7 0 1 .3 1 1v15c0-.7-.3-1-1-1H3zM21 4h-8c-.7 0-1 .3-1 1v15c0-.7.3-1 1-1h8z"/>',
 "metroidvania": '<path fill-rule="evenodd" d="M8 6a4 4 0 1 0 0 8 4 4 0 0 0 0-8zm0 2.5a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3z"/><path d="M12 9h9v3h-2v3h-2v-3h-5z"/>',
 "sports": '<path fill-rule="evenodd" d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zM12 8l3.5 2.5-1.3 4H9.8l-1.3-4z"/>',
}

GENRES = [  # id, подпись на бейдже, цвет, буквы для версии «с буквами»
 ("tower-defense", "Tower Defense", "3A9B68", "TD"),
 ("rpg",           "RPG",           "8B5CF6", "RP"),
 ("roguelike",     "Roguelike",     "B7791F", "Rg"),
 ("platformer",    "Platformer",    "E4572E", "Pf"),
 ("shooter",       "Shooter",       "C0392B", "Sh"),
 ("strategy",      "Strategy",      "2D84B0", "St"),
 ("survival",      "Survival",      "D9822B", "Sv"),
 ("sandbox",       "Sandbox",       "5E9E3A", "Sb"),
 ("puzzle",        "Puzzle",        "0E9AA7", "Pz"),
 ("horror",        "Horror",        "4B5563", "Hr"),
 ("racing",        "Racing",        "E11D48", "Rc"),
 ("simulation",    "Simulation",    "3B82F6", "Sm"),
 ("idle-clicker",  "Idle Clicker",  "CA8A04", "Ic"),
 ("card-game",     "Card Game",     "7C3AED", "Cg"),
 ("fighting",      "Fighting",      "DC2626", "Fg"),
 ("adventure",     "Adventure",     "16A34A", "Ad"),
 ("open-world",    "Open World",    "0891B2", "OW"),
 ("mmo",           "MMO",           "DB2777", "MM"),
 ("battle-royale", "Battle Royale", "EA580C", "BR"),
 ("moba",          "MOBA",          "1D4ED8", "Mb"),
 ("stealth",       "Stealth",       "374151", "Sl"),
 ("rhythm",        "Rhythm",        "C026D3", "Rh"),
 ("visual-novel",  "Visual Novel",  "F472B6", "VN"),
 ("metroidvania",  "Metroidvania",  "6D28D9", "Mv"),
 ("sports",        "Sports",        "15803D", "Sp"),
]

category = {
    "name": "Жанры",
    "slug": "genres",
    "items": [{"id": i, "label": l, "color": c, "icon": a, "svg": ICONS[i]} for i, l, c, a in GENRES],
}

cfg = json.loads(CFG.read_text(encoding="utf-8"))
cats = [c for c in cfg["categories"] if c["slug"] != "genres"]
pos = next((n + 1 for n, c in enumerate(cats) if c["name"] == "Игры"), len(cats))
cats.insert(pos, category)           # сразу после «Игры» (или в конец, если её нет)
cfg["categories"] = cats
CFG.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")

import build
build.build_all()
print(f"Категория «Жанры»: {len(GENRES)} бейджей добавлено.")
