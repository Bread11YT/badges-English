"""Добавляет Jupyter в «Языки» и новую категорию «Языки мира» (24 бейджа) в badges.json.

Положите рядом с build.py и badges.json, затем:  python add_languages.py
Скрипт сам пересоберёт все SVG, README.md и index.html (включая папки badges/colors/ЦВЕТ/).
Можно запускать повторно: ничего не задвоится.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CFG = ROOT / "badges.json"

# Иконка «перевод» (одна на все языки), сетка 24x24
TRANSLATE = '<path d="M12.87 15.07l-2.54-2.51.03-.03A17.52 17.52 0 0 0 14.07 6H17V4h-7V2H8v2H1v1.99h11.17C11.5 7.92 10.44 9.75 9 11.35 8.07 10.32 7.3 9.19 6.69 8h-2c.73 1.63 1.73 3.17 2.98 4.56l-5.09 5.02L4 19l5-5 3.11 3.11.76-2.04zM18.5 10h-2L12 22h2l1.12-3h4.75L21 22h2l-4.5-12zm-2.62 7l1.62-4.33L19.12 17h-3.24z"/>'

# Запасная иконка Jupyter, если icons/jupyter.svg почему-то нет
JUPYTER = ('<path d="M4 9c1.8-3.4 5-4.5 8-4.5s6.2 1.1 8 4.5c-2.3-1.6-5-2.2-8-2.2S6.3 7.4 4 9z"/>'
           '<path d="M4 15c2.3 1.6 5 2.2 8 2.2s5.7-.6 8-2.2c-1.8 3.4-5 4.5-8 4.5S5.8 18.4 4 15z"/>'
           '<path d="M12 9.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5zM19 2.2a1.4 1.4 0 1 0 0 2.8 1.4 1.4 0 0 0 0-2.8zM5 19a1.4 1.4 0 1 0 0 2.8A1.4 1.4 0 0 0 5 19z"/>')

LANGS = [  # id, подпись, цвет, код для версии «с буквами»
 ("russian",    "Russian",    "D52B1E", "RU"),
 ("english",    "English",    "1D4ED8", "EN"),
 ("spanish",    "Spanish",    "D97706", "ES"),
 ("french",     "French",     "2563EB", "FR"),
 ("german",     "German",     "4B5563", "DE"),
 ("italian",    "Italian",    "16A34A", "IT"),
 ("portuguese", "Portuguese", "15803D", "PT"),
 ("chinese",    "Chinese",    "DC2626", "ZH"),
 ("japanese",   "Japanese",   "E11D48", "JA"),
 ("korean",     "Korean",     "0891B2", "KO"),
 ("arabic",     "Arabic",     "047857", "AR"),
 ("hindi",      "Hindi",      "EA580C", "HI"),
 ("turkish",    "Turkish",    "B91C1C", "TR"),
 ("polish",     "Polish",     "BE185D", "PL"),
 ("ukrainian",  "Ukrainian",  "CA8A04", "UK"),
 ("dutch",      "Dutch",      "C2410C", "NL"),
 ("swedish",    "Swedish",    "0E7490", "SV"),
 ("vietnamese", "Vietnamese", "B45309", "VI"),
 ("indonesian", "Indonesian", "9F1239", "ID"),
 ("hebrew",     "Hebrew",     "3B82F6", "HE"),
 ("greek",      "Greek",      "0369A1", "EL"),
 ("czech",      "Czech",      "7C3AED", "CS"),
 ("thai",       "Thai",       "6D28D9", "TH"),
 ("persian",    "Persian",    "0F766E", "FA"),
]

cfg = json.loads(CFG.read_text(encoding="utf-8"))
cats = cfg["categories"]

# 1) Jupyter в «Языки»
langs = next((c for c in cats if c["slug"] == "languages"), None)
if langs is None:
    raise SystemExit("В badges.json нет категории со slug 'languages'.")
if not any(i["id"] == "jupyter" for i in langs["items"]):
    old = next((i for c in cats for i in c["items"] if i["id"] == "jupyter"), None)
    item = {"id": "jupyter", "label": "Jupyter",
            "color": old["color"] if old else "F37626",
            "icon": old["icon"] if old else "Jp"}
    if not (ROOT / "icons" / "jupyter.svg").exists():
        item["svg"] = JUPYTER
    langs["items"].append(item)
    print("Jupyter добавлен в «Языки».")
else:
    print("Jupyter в «Языки» уже есть.")

# 2) Языки мира
world = {"name": "Языки мира", "slug": "world-languages",
         "items": [{"id": i, "label": l, "color": c, "icon": a, "svg": TRANSLATE} for i, l, c, a in LANGS]}
cats = [c for c in cats if c["slug"] != "world-languages"]
pos = next((n + 1 for n, c in enumerate(cats) if c["slug"] == "languages"), len(cats))
cats.insert(pos, world)               # сразу после «Языки»
cfg["categories"] = cats
CFG.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")

import build
build.build_all()
print(f"Категория «Языки мира»: {len(LANGS)} бейджей добавлено.")
